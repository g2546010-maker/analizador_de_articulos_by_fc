"""
Script de prueba para ver extracción de metadatos en acción.
Ejecutar: python -m app.scripts.test_extraction
"""
from pathlib import Path
from app.services.pdf_service import PDFService
import json


def test_extraction():
    """Prueba extracción con PDFs reales"""
    pdf_service = PDFService()
    
    # PDFs de prueba
    base_path = Path(__file__).parent.parent.parent / 'pdf'
    
    # Probar con un artículo indexado (buscar el primero disponible)
    art_folder = base_path / 'art_rev_indexada'
    art_pdfs = list(art_folder.glob('*.pdf')) if art_folder.exists() else []
    art_path = art_pdfs[0] if art_pdfs else None
    
    if art_path and art_path.exists():
        print("="*80)
        print(f"Procesando: {art_path.name}")
        print("="*80)
        
        # Extraer metadatos
        metadata = pdf_service.extract_metadata(str(art_path))
        
        # Mostrar resultados
        print(f"\n✓ Extracción exitosa: {metadata['success']}")
        print(f"✓ Confianza: {metadata['confidence']*100:.1f}%\n")
        
        print("METADATOS EXTRAÍDOS:")
        print("-" * 80)
        
        print(f"\n📄 TÍTULO:")
        print(f"   {metadata['titulo'] or 'No encontrado'}")
        
        print(f"\n👥 AUTORES ({len(metadata['autores'])}):")
        for i, autor in enumerate(metadata['autores'][:5], 1):
            print(f"   {i}. {autor}")
        if len(metadata['autores']) > 5:
            print(f"   ... y {len(metadata['autores']) - 5} más")
        
        print(f"\n📅 AÑO:")
        print(f"   {metadata['anio_publicacion'] or 'No encontrado'}")
        
        print(f"\n🔗 DOI:")
        print(f"   {metadata['doi'] or 'No encontrado'}")
        
        print(f"\n📰 ISSN:")
        print(f"   {metadata['issn'] or 'No encontrado'}")
        
        print(f"\n📧 EMAILS ({len(metadata['emails'])}):")
        for email in metadata['emails'][:3]:
            print(f"   - {email}")
        
        print(f"\n📝 RESUMEN:")
        if metadata['resumen']:
            resumen = metadata['resumen'][:300] + "..." if len(metadata['resumen']) > 300 else metadata['resumen']
            print(f"   {resumen}")
        else:
            print("   No encontrado")
        
        print(f"\n🏷️ PALABRAS CLAVE ({len(metadata['palabras_clave'])}):")
        if metadata['palabras_clave']:
            print(f"   {', '.join(metadata['palabras_clave'][:10])}")
        else:
            print("   No encontradas")
        
        print("\n" + "="*80)
        
        # Info del PDF
        info = pdf_service.get_pdf_info(str(art_path))
        print(f"\nINFO DEL PDF:")
        print(f"   Páginas: {info['num_pages']}")
        print(f"   Tamaño: {info['file_size'] / 1024:.1f} KB")
        print(f"   Encriptado: {info['encrypted']}")
        
        if info['metadata'].get('title'):
            print(f"   Título (metadata): {info['metadata']['title']}")
        
        print("\n" + "="*80)
        
    else:
        print(f"❌ No se encontró el archivo: {art_path}")
    
    # Probar con un informe técnico
    print("\n\n")
    inf_folder = base_path / 'informe_tec'
    inf_pdfs = list(inf_folder.glob('*.pdf')) if inf_folder.exists() else []
    inf_path = inf_pdfs[0] if inf_pdfs else None
    
    if inf_path and inf_path.exists():
        print("="*80)
        print(f"Procesando: {inf_path.name}")
        print("="*80)
        
        metadata = pdf_service.extract_metadata(str(inf_path))
        
        print(f"\n✓ Extracción exitosa: {metadata['success']}")
        print(f"✓ Confianza: {metadata['confidence']*100:.1f}%\n")
        
        print("CAMPOS ENCONTRADOS:")
        print(f"   Título: {'✓' if metadata['titulo'] else '✗'}")
        print(f"   Autores: {'✓' if metadata['autores'] else '✗'} ({len(metadata['autores'])})")
        print(f"   Año: {'✓' if metadata['anio_publicacion'] else '✗'}")
        print(f"   DOI: {'✓' if metadata['doi'] else '✗'}")
        print(f"   ISSN: {'✓' if metadata['issn'] else '✗'}")
        print(f"   Resumen: {'✓' if metadata['resumen'] else '✗'}")
        
        if metadata['titulo']:
            print(f"\n📄 TÍTULO: {metadata['titulo'][:100]}...")
        
        print("\n" + "="*80)


if __name__ == '__main__':
    test_extraction()
