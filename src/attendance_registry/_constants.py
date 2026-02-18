class ERRORS:
    DATE_FORMAT = 'La fecha provista debe ser una cadena de texto o una tupla de dos cadenas de texto.'
    ONLY_DATETIMELIKE = 'El valor de fecha o rango de fecha debe ser [str], [date], [datetime] o una tupla de dos elementos de cualquiera de los tipos antes mencioanados.'
    TUPLE_INVALID_SIZE = 'Se debe usar una tupla con exactamente dos valores como rango de fecha.'
    INVALID_RANGE = 'La fecha inicial debe ser menor a la fecha final.'
    TUPLE_MUST_BE_SAME_TYPE = 'Ambos valores deben ser date [YYYY-MM-DD] o datetime [YYYY-MM-DD hh:mm:ss]'
    SCALAR_VALUE_MUST_BE_DATE_LIKE = 'Para usar una única fecha como rango, está debe tener estructura [aaaa-mm-dd] o ser de tipo [date]'

class REGEX:
    DATETIME_STRUCTURE = r'^\d{4}(-\d{2}){2}(\s|T)\d{2}(:\d{2}){2}$'
    DATE_STRUCTURE = r'^\d{4}(-\d{2}){2}$'

ENV_VAR_PREFIX = 'ATT_'
