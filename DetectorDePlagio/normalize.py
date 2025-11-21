# normalize_simple.py
# Normalizador simple: elimina comentarios y reemplaza nombres de variables por v1, v2, ...
# Compatible con C++, Java y Python.

import re

# Palabras clave comunes en varios lenguajes
KEYWORDS = {
    'if','else','for','while','do','switch','case','break','continue','return',
    'class','public','private','protected','static','void','int','float','double',
    'char','boolean','true','false','new','this','super','try','catch','finally',
    'import','package','include','using','namespace','def','lambda','var','const',
    'cout','cin','std','main'
}

IDENT_RE = re.compile(r'\b[_A-Za-z]\w*\b')

def remove_comments(code: str) -> str:
    """Elimina comentarios //, /* ... */, y #."""
    # Quitar comentarios tipo /* ... */
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    # Quitar comentarios de una línea //
    code = re.sub(r'//.*', '', code)
    # Quitar comentarios tipo #
    code = re.sub(r'#.*', '', code)
    return code

def normalize_variables(code: str) -> str:
    """Elimina comentarios y renombra variables."""
    code = remove_comments(code)

    mapping = {}
    counter = 1

    def repl(match):
        nonlocal counter
        word = match.group(0)
        # No tocar palabras clave
        if word in KEYWORDS:
            return word
        # Crear mapeo consistente
        if word not in mapping:
            mapping[word] = f"v{counter}"
            counter += 1
        return mapping[word]

    code = IDENT_RE.sub(repl, code)

    # Compactar espacios y líneas vacías
    code = re.sub(r'\s+', ' ', code).strip()

    return code

# Ejemplo de uso
if __name__ == "__main__":
    archivo = "archivo_1.txt"
    with open(archivo, "r", encoding="utf-8") as f:
        original = f.read()

    normalizado = normalize_variables(original)

    print("=== Código original ===")
    print(original)
    print("\n=== Código normalizado (sin comentarios y con variables renombradas) ===")
    print(normalizado)


# Ejemplo de uso
if __name__ == "__main__":
    archivo = "archivo_1.txt"
    with open(archivo, "r", encoding="utf-8") as f:
        original = f.read()

    normalizado = normalize_variables(original)

    print("=== Código original ===")
    print(original)
    print("\n=== Código con variables normalizadas ===")
    print(normalizado)
