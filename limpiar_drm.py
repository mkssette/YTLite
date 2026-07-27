import os
import re

def patch_github_actions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workflow_path = os.path.join(base_dir, ".github", "workflows", "_build_tweaks.yml")
    if not os.path.exists(workflow_path):
        print(f"[!] Error: No se encontró {workflow_path}")
        return False

    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Si ya está parcheado, omitir
    if "Build YouTube Plus (Local Source)" in content:
        print("[OK] GitHub Actions ya estaba parcheado (Libre de DRM).")
        return True

    # 1. Eliminar por completo el código de descarga malicioso
    pattern_download = r"\s*- name: Download YouTube Plus \(by version\).*?exit 1\n\s*fi"
    new_content = re.sub(pattern_download, "", content, flags=re.DOTALL)
    
    # 2. Insertar Build YouTube Plus DESPUÉS de Clone YouTubeHeader, y quitar el if de Clone YouTubeHeader
    pattern_header = r"\s*- name: Clone YouTubeHeader\n\s*if: \$\{\{.*?\}\}\n\s*run: \|"
    replacement_header = """
      - name: Clone YouTubeHeader
        run: |"""
    new_content = re.sub(pattern_header, replacement_header, new_content, count=1)

    # Buscar el final del bloque de Clone YouTubeHeader y añadir el Build
    pattern_build = r"(cp -r \"\$THEOS/include/YouTubeHeader\" \"\$THEOS/include/YTHeaders\"\n\s*fi)"
    replacement_build = r"""\1

      - name: Build YouTube Plus (Local Source)
        run: |
          make clean package DEBUG=0 FINALPACKAGE=1
          mv packages/*.deb ytplus.deb"""
    new_content = re.sub(pattern_build, replacement_build, new_content, count=1)

    # Arreglar el error de Homebrew en macos-latest
    pattern_brew = r"run: brew install make ldid dpkg"
    replacement_brew = """run: |
          export HOMEBREW_NO_REQUIRE_TAP_TRUST=1
          brew untap aws/tap || true
          brew install make ldid dpkg"""
    new_content = re.sub(pattern_brew, replacement_brew, new_content)

    # Arreglar la falta de actions/checkout (sin lo cual no se puede compilar el código fuente)
    pattern_checkout = r"\s*steps:\s*- name: Install Dependencies"
    replacement_checkout = """
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Install Dependencies"""
    new_content = re.sub(pattern_checkout, replacement_checkout, new_content)

    if new_content == content:
        print("[!] Advertencia: No se encontró el código malicioso en GitHub Actions. ¿Tal vez el desarrollador cambió el código?")
    else:
        with open(workflow_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print("[EXCELENTE] Script de GitHub Actions parcheado. Ahora compilará tu código fuente limpio.")
    
    return True


def patch_settings():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, "Settings.x")
    if not os.path.exists(settings_path):
        print(f"[!] Error: No se encontró {settings_path}")
        return False

    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "SupportDevelopment" not in content:
        print("[OK] El menú de Donaciones/Sponsors ya estaba eliminado en Settings.x.")
        return True

    # Patrón para borrar el bloque de la variable "support" (Donaciones)
    pattern_support = r"\s*YTSettingsSectionItem \*support = \[\%c\(YTSettingsSectionItem\) itemWithTitle:LOC\(@\"SupportDevelopment\"\).*?return YES;\n\s*\}\];"
    # Patrón para borrar la línea donde se añade la sección
    pattern_add = r"\s*\[sectionItems addObject:support\];"

    new_content = re.sub(pattern_support, "", content, flags=re.DOTALL)
    new_content = re.sub(pattern_add, "", new_content)

    if new_content == content:
        print("[!] Advertencia: No se pudo eliminar la sección de donaciones. ¿Tal vez cambió el formato?")
    else:
        with open(settings_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print("[EXCELENTE] Muro de donaciones eliminado exitosamente de Settings.x.")
    
    return True


def patch_roothide():
    header_path = os.path.join("Utils", "NSBundle+YTLite.h")
    if not os.path.exists(header_path):
        print(f"[!] Error: No se encontró {header_path}")
        return False

    with open(header_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "#if __has_include(<roothide.h>)" in content:
        print("[OK] El parche de roothide.h ya estaba aplicado.")
        return True

    pattern = r"#import <roothide\.h>"
    replacement = """#if __has_include(<roothide.h>)
#import <roothide.h>
#else
#define jbroot(path) path
#endif"""

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        print("[!] Advertencia: No se encontró '#import <roothide.h>'.")
    else:
        with open(header_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print("[EXCELENTE] Dependencia de roothide.h solucionada.")

    return True


if __name__ == "__main__":
    print("="*50)
    print("   🛡️  YTLite / YTPlus - ELIMINADOR DE DRM  🛡️")
    print("="*50)
    print("Aplicando parches para liberar tu aplicación...\n")
    
    patch_github_actions()
    patch_settings()
    patch_roothide()
    
    print("\n" + "="*50)
    print("✅ Proceso terminado. ¡Tu repositorio está limpio!")
    print("👉 Recuerda subir (hacer commit y push) los cambios a tu GitHub.")
    print("="*50)
    input("Presiona Enter para salir...")
