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

    # Eliminar ambos bloques de descarga maliciosos y poner compilación local
    # Buscamos desde el paso "Download YouTube Plus (by version)" hasta el "fi" del paso por URL.
    pattern = r"\s*- name: Download YouTube Plus \(by version\).*?exit 1\n\s*fi"
    
    replacement = """
      - name: Build YouTube Plus (Local Source)
        run: |
          make clean package DEBUG=0 FINALPACKAGE=1
          mv packages/*.deb ytplus.deb"""

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
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


if __name__ == "__main__":
    print("="*50)
    print("   🛡️  YTLite / YTPlus - ELIMINADOR DE DRM  🛡️")
    print("="*50)
    print("Aplicando parches para liberar tu aplicación...\n")
    
    patch_github_actions()
    patch_settings()
    
    print("\n" + "="*50)
    print("✅ Proceso terminado. ¡Tu repositorio está limpio!")
    print("👉 Recuerda subir (hacer commit y push) los cambios a tu GitHub.")
    print("="*50)
    input("Presiona Enter para salir...")
