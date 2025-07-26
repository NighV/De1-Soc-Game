#!/usr/bin/env python3
"""
Conversor PNG para Sprite - Versão Otimizada
Converte imagens PNG para arrays C com valores RGB565 em hexadecimal.
Suporta transparência e não limita às cores predefinidas.
"""

from PIL import Image
import sys
import os

def rgb_to_rgb565(r, g, b):
    """
    Converte RGB (8 bits por canal) para RGB565 (16 bits total).
    
    Args:
        r, g, b: Valores RGB de 0-255
    
    Returns:
        Valor RGB565 como uint16
    """
    # Reduz os bits: R(8->5), G(8->6), B(8->5)
    r5 = (r >> 3) & 0x1F  # 5 bits para vermelho
    g6 = (g >> 2) & 0x3F  # 6 bits para verde
    b5 = (b >> 3) & 0x1F  # 5 bits para azul
    
    # Combina em formato RGB565
    return (r5 << 11) | (g6 << 5) | b5

def converter_png_para_sprite(caminho_imagem, nome_sprite):
    """
    Converte PNG para sprite C com valores hexadecimais RGB565.
    Suporta transparência (pixels transparentes viram 0x0000 - preto).
    
    Args:
        caminho_imagem: Caminho para o arquivo PNG
        nome_sprite: Nome da variável do sprite
    
    Returns:
        tuple: (codigo_c, largura, altura) ou (None, 0, 0) em caso de erro
    """
    try:
        print(f"🎨 Abrindo PNG: {caminho_imagem}")
        img = Image.open(caminho_imagem)
        
        # Converte para RGBA para lidar com transparência
        if img.mode != 'RGBA':
            print(f"📝 Convertendo de {img.mode} para RGBA...")
            img = img.convert('RGBA')
        
        largura, altura = img.size
        print(f"📏 Dimensões: {largura}x{altura} pixels")
        
        # Estatísticas das cores
        cores_usadas = set()
        pixels_transparentes = 0
        
        # Gera o cabeçalho do array
        resultado = f"uint16_t {nome_sprite}[{largura} * {altura}] = {{\n"
        
        # Processa cada pixel
        for y in range(altura):
            linha = "    "
            for x in range(largura):
                r, g, b, a = img.getpixel((x, y))
                
                # Se pixel é transparente (alpha < 128), usa cor transparente especial
                if a < 128:
                    linha += "0xF8FF, "  # Cor especial para transparência
                    pixels_transparentes += 1
                else:
                    # Converte para RGB565
                    rgb565 = rgb_to_rgb565(r, g, b)
                    linha += f"0x{rgb565:04X}, "
                    cores_usadas.add(rgb565)
            
            # Remove a última vírgula e adiciona quebra de linha
            linha = linha.rstrip(", ") + ",\n"
            resultado += linha
        
        # Remove a última vírgula e fecha o array
        resultado = resultado.rstrip(",\n") + "\n};\n"
        
        # Estatísticas
        print(f"🎨 Cores únicas encontradas: {len(cores_usadas)}")
        print(f"👻 Pixels transparentes: {pixels_transparentes}")
        
        return resultado, largura, altura
        
    except Exception as e:
        print(f"❌ Erro ao processar a imagem: {e}")
        return None, 0, 0

def mostrar_preview_cores(caminho_imagem, max_cores=10):
    """
    Mostra uma prévia das cores mais usadas na imagem.
    """
    try:
        img = Image.open(caminho_imagem)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Conta as cores
        contagem_cores = {}
        largura, altura = img.size
        
        for y in range(altura):
            for x in range(largura):
                r, g, b, a = img.getpixel((x, y))
                if a >= 128:  # Não transparente
                    rgb565 = rgb_to_rgb565(r, g, b)
                    contagem_cores[rgb565] = contagem_cores.get(rgb565, 0) + 1
        
        # Ordena por frequência
        cores_ordenadas = sorted(contagem_cores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"🎨 Cores mais usadas na imagem:")
        for i, (cor, count) in enumerate(cores_ordenadas[:max_cores]):
            # Converte de volta para RGB para mostrar
            r = (cor >> 11) & 0x1F
            g = (cor >> 5) & 0x3F
            b = cor & 0x1F
            r_8bit = (r << 3) | (r >> 2)
            g_8bit = (g << 2) | (g >> 4)
            b_8bit = (b << 3) | (b >> 2)
            
            print(f"  {i+1}. 0x{cor:04X} - RGB({r_8bit:3}, {g_8bit:3}, {b_8bit:3}) - {count} pixels")
            
    except Exception as e:
        print(f"⚠️ Não foi possível analisar as cores: {e}")

def main():
    if len(sys.argv) < 3:
        print("🖼️  CONVERSOR PNG PARA SPRITE")
        print("=" * 40)
        print("Converte imagens PNG para arrays C com valores RGB565 em hexadecimal.")
        print("Não limita às cores predefinidas - usa cores exatas da imagem!")
        print()
        print("Uso: python png_to_sprite.py <arquivo.png> <nome_sprite> [--preview]")
        print()
        print("Exemplos:")
        print("  python png_to_sprite.py turtle.png TurtleSprite")
        print("  python png_to_sprite.py player.png PlayerSprite --preview")
        print()
        print("Opções:")
        print("  --preview: Mostra prévia das cores antes de converter")
        sys.exit(1)
    
    caminho_imagem = sys.argv[1]
    nome_sprite = sys.argv[2]
    mostrar_preview = "--preview" in sys.argv
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"❌ Erro: Arquivo '{caminho_imagem}' não encontrado.")
        sys.exit(1)
    
    # Verifica se é PNG
    if not caminho_imagem.lower().endswith('.png'):
        print(f"⚠️  Aviso: O arquivo não tem extensão .png")
        print("   Continuando mesmo assim...")
    
    print(f"🔄 Convertendo '{caminho_imagem}' para sprite '{nome_sprite}'...")
    print(f"📋 Modo: Valores RGB565 hexadecimais exatos (sem limitação de cores)")
    print()
    
    # Mostra prévia das cores se solicitado
    if mostrar_preview:
        mostrar_preview_cores(caminho_imagem)
        print()
    
    # Converte a imagem
    resultado, largura, altura = converter_png_para_sprite(caminho_imagem, nome_sprite)
    
    if resultado:
        # Salva o resultado em um arquivo
        nome_arquivo_saida = f"{nome_sprite}.c"
        with open(nome_arquivo_saida, 'w') as f:
            f.write(f"// Sprite: {nome_sprite}\n")
            f.write(f"// Tamanho: {largura}x{altura} pixels\n")
            f.write(f"// Arquivo original: {caminho_imagem}\n")
            f.write(f"// Formato: RGB565 hexadecimal\n")
            f.write(f"// Gerado automaticamente em {sys.argv[0]}\n\n")
            f.write(resultado)
        
        print(f"✅ Sprite salvo em '{nome_arquivo_saida}'")
        print(f"📊 Informações:")
        print(f"   • Tamanho: {largura}x{altura} pixels")
        print(f"   • Total de pixels: {largura * altura}")
        print(f"   • Tamanho do array: {largura * altura * 2} bytes")
        print()
        print(f"📝 Para usar no seu código C:")
        print(f"   entidade->sprite = {nome_sprite};")
        print(f"   entidade->tamanhoSpriteX = {largura};")
        print(f"   entidade->tamanhoSpriteY = {altura};")
        print()
        print("🎯 Prévia do array:")
        linhas = resultado.split('\n')
        for i, linha in enumerate(linhas[:6]):  # Mostra primeiras 6 linhas
            print(f"   {linha}")
        if len(linhas) > 6:
            print(f"   ... (mais {len(linhas) - 6} linhas)")
        
    else:
        print("❌ Falha na conversão.")
        sys.exit(1)

if __name__ == "__main__":
    main()
