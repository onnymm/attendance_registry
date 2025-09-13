# attendance_registry
Pequeña librería diseñada para obtener registros de asistencia desde dispositivos HikVision de forma remota a través de su API

### Instalación

```bash
pip install git+https://github.com/onnymm/attendance_registry.git
```

### Configuración
Crea un archivo `.env` con los siguientes datos
```env
COOKIE = 12345678-90ab-cdef-ghij-klmnopqrstuv
SITE_ID = wxyz1234567890abcdefghijklmnopqr
TOKEN = st.uvwxyz12345967890abcdefghijklm-nopqrstuvw-xyz1234-567890abc
DEVICE_MODEL = MY-DEVICE-MODEL-123
```

Posteriormente importa el módulo junto con la clase `Literal` desde typing:
```py
from src.attendance_registry import Assistance
from typing import Literal
```

Crea un conjunto de literales que nombren tus dispositivos, por ejemplo:
```py
DEVICES = Literal['device_1', 'device_2']
```

Inicializa una instancia e indexa tu conjunto de literales como genérico de la clase
```py
registry = Assistance[DEVICES](...)
```

Como parámetro de entrada colocarás un diccionario que tendrá como llaves los nombres de tus literales y como valores los números de serie de tus dispositivos. Notarás que el diccionario autocompleta las llaves.

```py
Assistance[DEVICES](
    {
        'device_1': 'SN123456',
        'device_2': 'SN789012',
    }
)
```

La instancia ha sido creada y lista para usarse.

## Métodos
### `get_today_attendance` Obtención de los registros de asistencia del hoy

Este método obtiene los registros de asistencia del día de hoy, ya sea de un dispositivo
especificado o de todos los dispositivos.

Uso:
```py
# Obtención de los registros del día de hoy
data = instance.get_today_attendance()

# Obtención de los registros del día de hoy por dispositivo específico
data = instance.get_today_attendance('my_device_name')
```

### `get_daily_attendance` Obtención de registros diarios de asistencia
Este método obtiene todos los registros de asistencia de un día especificado o
un rango de fecha especificado con granularidad de día y opcionalmente
especificando un dispositivo.

Uso:
```py
# Obtención de los registros de un día especificado
data = instance.get_daily_attendance('2025-08-21')

# Obtención de los registros de un rango de fecha
data = instance.get_daily_attendance(('2025-08-01', '2025-08-31'))

# Obtención de los registros de un día por dispositivo específico
data = instance.get_today_attendance('2025-08-21', 'my_device_name')
```
