# 📘 Prefect 3 – Guía completa de Deploy  
### (con equivalencias directas a Prefect 2)

Este documento resume **en un solo flujo** cómo desplegar y ejecutar un *flow* en **Prefect 3**, y muestra el **equivalente exacto** de cada paso en **Prefect 2** (como en cursos antiguos, por ejemplo DataCamp).

---

## 1️⃣ Iniciar el servidor Prefect

### Prefect 3
```bash
prefect server start
Configurar la API (solo una vez):

bash
Copiar código
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
Prefect 2 (equivalente)
bash
Copiar código
prefect server start
2️⃣ Crear un Work Pool (antes: Agent Pool)
Prefect 3
bash
Copiar código
prefect work-pool create my-process-pool --type process
Listar pools:

bash
Copiar código
prefect work-pool ls
Prefect 2 (antiguo)
bash
Copiar código
prefect work-pool create default-agent-pool
3️⃣ Iniciar Worker / Agent
Prefect 3
bash
Copiar código
prefect worker start --pool my-process-pool
Prefect 2 (eliminado en Prefect 3)
bash
Copiar código
prefect agent start -p default-agent-pool
4️⃣ Crear un Deployment
Prefect 3 (comando correcto)
bash
Copiar código
prefect deploy main.py:ml_workflow \
  --name ml_workflow_bank_churn \
  --pool my-process-pool \
  --tag dev
Cuando aparezca la pregunta:

text
Copiar código
Would you like your workers to pull your flow code from a remote storage location?
Responder:

text
Copiar código
n
(Se asume código local, como en el curso).

Prefect 2 (comando antiguo)
bash
Copiar código
prefect deployment build main.py:ml_workflow \
  -n ml_workflow_bank_churn \
  -t dev \
  -a
5️⃣ Listar Deployments
Prefect 3
bash
Copiar código
prefect deployment ls
Salida típica:

text
Copiar código
ml-workflow/ml_workflow_bank_churn
⚠️ Nota: Prefect 3 normaliza el nombre del flow (_ → -).

6️⃣ Ejecutar un Deployment
Prefect 3
bash
Copiar código
prefect deployment run ml-workflow/ml_workflow_bank_churn
Prefect 2
bash
Copiar código
prefect deployment run ml_workflow/ml_workflow_bank_churn
7️⃣ Ver ejecución y logs
Los logs aparecen en la terminal donde corre el worker

Opcional:

bash
Copiar código
prefect flow-run inspect <FLOW_RUN_ID>