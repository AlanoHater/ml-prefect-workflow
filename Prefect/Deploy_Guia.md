# 📘 Prefect 3 – Guía completa de Deploy  
### (con equivalencias directas a Prefect 2)

Este documento resume **en un solo flujo** cómo desplegar y ejecutar un *flow* en **Prefect 3**, y muestra el **equivalente exacto** de cada paso en **Prefect 2** (como en cursos antiguos, por ejemplo DataCamp).

---

## 1️⃣ Iniciar el servidor Prefect

### Prefect 3
```bash
prefect server start
```

Configurar la API (solo una vez):
```bash
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

### Prefect 2 (equivalente)
```bash
prefect server start
```

---

## 2️⃣ Crear un Work Pool (antes: Agent Pool)

### Prefect 3
```bash
prefect work-pool create my-process-pool --type process
```

Listar pools:
```bash
prefect work-pool ls
```

### Prefect 2 (antiguo)
```bash
prefect work-pool create default-agent-pool
```

---

## 3️⃣ Iniciar Worker / Agent

### Prefect 3
```bash
prefect worker start --pool my-process-pool
```

### Prefect 2 (eliminado en Prefect 3)
```bash
prefect agent start -p default-agent-pool
```

---

## 4️⃣ Crear un Deployment

### Prefect 3 (comando correcto)
```bash
prefect deploy main.py:ml_workflow \
  --name ml_workflow_bank_churn \
  --pool my-process-pool \
  --tag dev
```

Cuando aparezca la pregunta:
```text
Would you like your workers to pull your flow code from a remote storage location?
```

Responder:
```text
n
```

(Se asume código local, como en el curso).

---

### Prefect 2 (comando antiguo)
```bash
prefect deployment build main.py:ml_workflow \
  -n ml_workflow_bank_churn \
  -t dev \
  -a
```

---

## 5️⃣ Listar Deployments

### Prefect 3
```bash
prefect deployment ls
```

Salida típica:
```text
ml-workflow/ml_workflow_bank_churn
```

⚠️ Nota: Prefect 3 normaliza el nombre del flow (`_` → `-`).

---

## 6️⃣ Ejecutar un Deployment

### Prefect 3
```bash
prefect deployment run ml-workflow/ml_workflow_bank_churn
```

### Prefect 2
```bash
prefect deployment run ml_workflow/ml_workflow_bank_churn
```

---

## 7️⃣ Ver ejecución y logs

- Los logs aparecen en la terminal donde corre el worker
- Opcional:
```bash
prefect flow-run inspect <FLOW_RUN_ID>
```

---

## 🔁 Tabla de equivalencias rápidas

| Prefect 2 (curso antiguo) | Prefect 3 (actual) |
|---------------------------|-------------------|
| prefect agent start | prefect worker start |
| default-agent-pool | work pool (process) |
| deployment build | prefect deploy |
| -a / --apply | implícito |
| agent | worker |
| Storage implícito | Pregunta interactiva (n) |

---

## ✅ Estado mínimo correcto en Prefect 3

- Servidor Prefect activo  
- PREFECT_API_URL configurado  
- Work pool creado  
- Worker corriendo  
- Deployment registrado  
- Flow run ejecutándose  

---

Este flujo es **funcionalmente equivalente** a lo que muestran los cursos basados en Prefect 2, pero usando el **CLI correcto de Prefect 3**.
