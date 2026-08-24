# Plano: Integração do Azure AI Search com Foundry

## Visão Geral
Adicionar capacidades de busca full-text, vetorial e híbrida ao projeto Foundry através do Azure AI Search com acesso via Managed Identity, sem depender de admin keys ou query keys no código.

Arquivo alvo principal: `infra/main.bicep`.

### Estado atual do template
- O Foundry account já usa `identity: { type: 'SystemAssigned' }`.
- O Foundry project também já usa `identity: { type: 'SystemAssigned' }`.
- Ainda faltam o recurso `Microsoft.Search/searchServices`, a connection do Foundry para o Search, os role assignments e os outputs do Search.

---

## 1. SERVIÇO AZURE AI SEARCH

### 1.1 Configuração Proposta

| Aspecto | Recomendação | Justificativa |
|--------|--------------|--------------|
| **SKU** | Basic inicialmente, parametrizado para Standard | Reduz custo no hack; Standard pode ser usado se o laboratório precisar de mais capacidade/recursos |
| **Replica** | 1 (mín. para dev) | Suficiente para hackathon |
| **Partition** | 1 (padrão) | Índices de tamanho moderado |
| **Identidade** | SystemAssigned | Útil para cenários futuros com indexers/datasources; o acesso do Foundry virá das MIs do Foundry |
| **Acesso de Rede** | enabled | Público (pode ser restrito depois) |

### 1.2 Recurso Bicep
```bicep
param searchServiceName string = 'search-hack-${suffix}'
@allowed([
  'basic'
  'standard'
])
param searchSkuName string = 'basic'

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  sku: { name: searchSkuName }
  identity: { type: 'SystemAssigned' }
  tags: tags
  properties: {
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
  }
}
```

### 1.3 Considerações de Design
- ✅ **Vector Search**: Suportado nativamente (habilitado por padrão)
- ✅ **Semantic Search**: Requer tier S1 ou superior
- ✅ **AI Enrichment**: Integração com Foundry/OpenAI para embeddings
- ✅ **Escalabilidade**: Adicionar replicas conforme demanda

---

## 2. PERMISSÕES DE MANAGED IDENTITY

### 2.1 Identidades Envolvidas

```
┌──────────────────┐
│   Foundry        │ (SystemAssigned MI)
│   Account        │─────────┐
└──────────────────┘         │
                             ├──► Search Service
┌──────────────────┐         │
│   Project        │ (SystemAssigned MI)
│   (Foundry)      │─────────┘
└──────────────────┘
```

### 2.2 Roles Necessárias

| Identidade | Role | Permissões | Escopo |
|-----------|------|-----------|--------|
| **Foundry Account** | `Search Service Contributor` | Criar/editar objetos de Search como índices, indexers, skillsets e aliases | Search Service |
| **Foundry Account** | `Search Index Data Contributor` | Carregar documentos, atualizar conteúdo e consultar índices | Search Service |
| **Foundry Project** | `Search Service Contributor` | Permitir operações administrativas feitas no contexto do projeto | Search Service |
| **Foundry Project** | `Search Index Data Contributor` | Manipular documentos e consultar índices no contexto do projeto | Search Service |

IDs oficiais das roles:

```bicep
var searchServiceContributorRoleId = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
var searchIndexDataContributorRoleId = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
var searchIndexDataReaderRoleId = '1407120a-92aa-4202-b7e9-c0e197c71c8f'
```

Observação: para um agente que só consulta índices, usar `Search Index Data Reader` em vez de `Search Index Data Contributor`.

### 2.3 Implementação em Bicep

```bicep
// Foundry account: gerenciar objetos de Search
resource foundrySearchServiceContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: searchService
  name: guid(searchService.id, foundry.id, searchServiceContributorRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchServiceContributorRoleId)
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Foundry account: carregar documentos e consultar indices
resource foundrySearchDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: searchService
  name: guid(searchService.id, foundry.id, searchIndexDataContributorRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexDataContributorRoleId)
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Foundry project: gerenciar objetos de Search no contexto do projeto
resource projectSearchServiceContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: searchService
  name: guid(searchService.id, project.id, searchServiceContributorRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchServiceContributorRoleId)
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Foundry project: carregar documentos e consultar indices
resource projectSearchDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: searchService
  name: guid(searchService.id, project.id, searchIndexDataContributorRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexDataContributorRoleId)
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
```

---

## 3. CASOS DE USO & PERMISSÕES GRANULARES

### 3.1 Use Case: Indexação de Documentos (Callcenter)

```
Foundry Agent (Call Center) 
    ↓
[Processa documentos, extrai embeddings via OpenAI]
    ↓
Search Service (Cria/atualiza índices)
    ↓
Permissão Necessária: "Search Index Data Contributor"
```

**Operações Permitidas:**
- Criar índice: `PUT /indexes/{indexName}`
- Adicionar documentos: `POST /docs/index`
- Atualizar esquema: `PUT /indexes/{indexName}`

---

### 3.2 Use Case: Consulta de Índices (Smart Farm)

```
Foundry Agent (Smart Farm)
    ↓
[Consulta para encontrar documentos similares]
    ↓
Search Service (Query com vector/semantic)
    ↓
Permissão Necessária: "Search Index Data Reader"
```

**Operações Permitidas:**
- Pesquisar: `POST /indexes/{indexName}/docs/search`
- Sugerir completions: `POST /indexes/{indexName}/docs/suggest`

---

## 4. CONEXÃO E CONFIGURAÇÃO DO FOUNDRY

### 4.1 Connection String para Foundry

Adicionar connection no projeto Foundry:

```bicep
resource searchConnection 'Microsoft.CognitiveServices/accounts/connections@2025-06-01' = {
  parent: foundry
  name: 'search-conn'
  properties: {
    category: 'CognitiveSearch'
    target: searchService.id
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: searchService.id
      Endpoint: 'https://${searchService.name}.search.windows.net'
    }
  }
}
```

Ponto de validação: confirmar no portal/API do Foundry se a categoria esperada para a connection é `CognitiveSearch` ou `AzureSearch`, pois esse contrato pode variar por versão de API.

### 4.2 Saídas Importantes

```bicep
output searchServiceName string = searchService.name
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'
output searchResourceId string = searchService.id
```

---

## 5. SEGURANÇA & BOAS PRÁTICAS

### 5.1 Implementado ✅
- **Managed Identity**: Sem necessidade de armazenar chaves
- **RBAC**: Roles específicas por permissão
- **Auditoria**: Azure Activity Log (já incluído via Application Insights)

### 5.2 Melhorias Futuras 🔮
| Melhoria | Impacto | Esforço |
|---------|--------|--------|
| Private Endpoint | Segurança network (Zero Trust) | Médio |
| Customer-Managed Keys (CMK) | Conformidade regulatória | Médio |
| IP Whitelist | Restringir acesso origem | Baixo |
| Encryption at Rest | Dados em repouso | Baixo |

---

## 6. CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Infraestrutura (Bicep)
- [ ] Adicionar recurso Search Service
- [ ] Configurar SystemAssigned Identity
- [ ] Criar role assignments (Foundry Account + Project)
- [ ] Adicionar connection ao projeto Foundry
- [ ] Atualizar outputs do template

### Fase 2: Integração Foundry
- [ ] Confirmar connection no Foundry Portal
- [ ] Testar autenticação via Managed Identity
- [ ] Validar permissões (criar índice, consultar)

### Fase 3: Validação
- [ ] Criar índice de teste via agente Foundry
- [ ] Indexar documentos sample (call center + farm data)
- [ ] Executar semantic search query
- [ ] Monitorar via Application Insights

### Fase 4: Documentação
- [ ] Adicionar guia de uso para participantes do hack
- [ ] Documentar esquema de índices
- [ ] Exemplos de query (Python/JavaScript)

---

## 7. CUSTO ESTIMADO (Azure Search)

| SKU | Custo/Mês | Indexação | Vector Search |
|-----|-----------|-----------|----------------|
| S0  | ~$250     | ✅ 1000 docs/sec | ✅ Nativo |
| S1  | ~$2,500   | ✅ 2000 docs/sec | ✅ Nativo |
| S2  | ~$12,500  | ✅ 3000 docs/sec | ✅ Nativo |

**Recomendação para Hack**: Começar com **S0** e monitorar.

---

## 8. COMANDOS ÚTEIS

### Listar Índices (Azure CLI)
```bash
az search index list \
  --resource-group <rg> \
  --service-name <search-name>
```

### Criar Índice via SDK Python
```python
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SearchClient(
    endpoint="https://<search-name>.search.windows.net",
    index_name="documents",
    credential=credential
)

# Busca vetorial
results = client.search(
    search_text="*",
    vector_queries=[{
        "kind": "vector",
        "k": 5,
        "fields": "embedding",
        "value": [embedding_vector]
    }]
)
```

---

## Próximos Passos

1. **Revisar e aprovar** este plano
2. **Atualizar main.bicep** com recursos de Search
3. **Testar deployment** em ambiente dev
4. **Documentar permissões** para participantes
5. **Validar integração** Foundry ↔ Search

