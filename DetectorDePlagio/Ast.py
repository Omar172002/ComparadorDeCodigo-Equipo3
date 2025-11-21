# ast.py
# Muestra el AST de un archivo (.cpp, .java o .txt) usando Tree-sitter.
# Incluye los valores (símbolos y texto real) del código fuente.
# También puede ser importado para obtener el AST y el código fuente.

from tree_sitter import Parser
from tree_sitter_languages import get_language

# Cambia según el lenguaje que quieras usar: "cpp" o "java"
DEFAULT_LANG = "cpp"

# --- Funciones auxiliares de análisis y visualización ---

def node_text(node, src: bytes) -> str:
    """Devuelve el texto exacto del nodo (operadores, literales, identificadores...)."""
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

def should_show_lexeme(node) -> bool:
    """Decide si mostrar el texto literal del nodo."""
    if len(node.children) == 0:
        return True
    return node.type in {
        "identifier", "type_identifier", "field_identifier",
        "string_literal", "char_literal", "number_literal"
    }

def print_tree_with_lexemes(node, src: bytes, depth: int = 0):
    """Imprime el árbol con los tipos y valores del código."""
    text = node_text(node, src).strip()
    show_value = should_show_lexeme(node)
    label = node.type
    if show_value and text:
        text = " ".join(text.split())
        if len(text) > 50:
            text = text[:50] + "…"
        label += f" ({text})"
    print("  " * depth + f"- {label}")
    for child in node.children:
        print_tree_with_lexemes(child, src, depth + 1)

def get_ast_root(file_path: str):
    """Devuelve el nodo raíz y el código fuente del AST de un archivo."""
    lang = get_language(DEFAULT_LANG)
    parser = Parser()
    parser.set_language(lang)
    with open(file_path, "rb") as f:
        code = f.read()
    tree = parser.parse(code)
    return tree.root_node, code

# --- Ejecución directa ---
if __name__ == "__main__":
    file_path = "archivo_2.txt"
    root, code = get_ast_root(file_path)
    print(f"\n=== AST ({DEFAULT_LANG}) con valores ===\n")
    print_tree_with_lexemes(root, code)
