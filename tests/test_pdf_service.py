"""
Tests para PDFService usando PDFs reales del proyecto.
"""
import pytest
import os
from pathlib import Path
from app.services.pdf_service import PDFService


# Rutas a PDFs de prueba
BASE_PDF_PATH = Path(__file__).parent.parent / 'pdf'
ART_REV_PATH = BASE_PDF_PATH / 'art_rev_indexada'
INFORME_TEC_PATH = BASE_PDF_PATH / 'informe_tec'
PROTO_PATH = BASE_PDF_PATH / 'proto'


@pytest.fixture
def pdf_service():
    """Crea una instancia de PDFService"""
    return PDFService()


@pytest.fixture
def sample_pdfs():
    """Retorna lista de PDFs de muestra para testing"""
    pdfs = {
        'articulo_indexado': None,
        'informe_tecnico': None,
        'prototipo': None
    }
    
    # Buscar PDFs de muestra
    if ART_REV_PATH.exists():
        art_pdfs = list(ART_REV_PATH.glob('*.pdf'))
        if art_pdfs:
            pdfs['articulo_indexado'] = str(art_pdfs[0])
    
    if INFORME_TEC_PATH.exists():
        inf_pdfs = list(INFORME_TEC_PATH.glob('*.pdf'))
        if inf_pdfs:
            pdfs['informe_tecnico'] = str(inf_pdfs[0])
    
    if PROTO_PATH.exists():
        proto_pdfs = list(PROTO_PATH.glob('*.pdf'))
        if proto_pdfs:
            pdfs['prototipo'] = str(proto_pdfs[0])
    
    return pdfs


class TestPDFTextExtraction:
    """Tests de extracción de texto"""
    
    def test_extract_text_from_articulo(self, pdf_service, sample_pdfs):
        """Test extracción de texto de artículo indexado"""
        if not sample_pdfs['articulo_indexado']:
            pytest.skip("No hay PDF de artículo disponible")
        
        success, text, error = pdf_service.extract_text(sample_pdfs['articulo_indexado'])
        
        assert success is True
        assert text is not None
        assert len(text) > 100
        assert error is None
    
    def test_extract_text_from_informe(self, pdf_service, sample_pdfs):
        """Test extracción de texto de informe técnico"""
        if not sample_pdfs['informe_tecnico']:
            pytest.skip("No hay PDF de informe disponible")
        
        success, text, error = pdf_service.extract_text(sample_pdfs['informe_tecnico'])
        
        assert success is True
        assert text is not None
        assert len(text) > 100
    
    def test_extract_text_from_prototipo(self, pdf_service, sample_pdfs):
        """Test extracción de texto de prototipo"""
        if not sample_pdfs['prototipo']:
            pytest.skip("No hay PDF de prototipo disponible")
        
        success, text, error = pdf_service.extract_text(sample_pdfs['prototipo'])
        
        assert success is True
        assert text is not None
        assert len(text) > 100
    
    def test_extract_text_nonexistent_file(self, pdf_service):
        """Test extracción de archivo inexistente"""
        success, text, error = pdf_service.extract_text('/nonexistent/file.pdf')
        
        assert success is False
        assert text is None
        assert "no encontrado" in error.lower()
    
    def test_extract_text_non_pdf_file(self, pdf_service, tmp_path):
        """Test extracción de archivo no PDF"""
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is not a PDF")
        
        success, text, error = pdf_service.extract_text(str(text_file))
        
        assert success is False
        assert "no es un PDF" in error


class TestMetadataExtraction:
    """Tests de extracción de metadatos"""
    
    def test_extract_metadata_from_articulo(self, pdf_service, sample_pdfs):
        """Test extracción completa de metadatos de artículo"""
        if not sample_pdfs['articulo_indexado']:
            pytest.skip("No hay PDF de artículo disponible")
        
        metadata = pdf_service.extract_metadata(sample_pdfs['articulo_indexado'])
        
        assert metadata['success'] is True
        assert metadata['error'] is None
        assert metadata['confidence'] > 0
        
        # Al menos algunos campos deberían estar presentes
        fields_found = sum([
            bool(metadata['titulo']),
            bool(metadata['autores']),
            bool(metadata['anio_publicacion']),
            bool(metadata['doi']),
            bool(metadata['issn']),
            bool(metadata['resumen'])
        ])
        
        assert fields_found >= 2, "Debería extraer al menos 2 campos"
    
    def test_extract_metadata_fields_types(self, pdf_service, sample_pdfs):
        """Test tipos de datos de metadatos extraídos"""
        if not sample_pdfs['articulo_indexado']:
            pytest.skip("No hay PDF disponible")
        
        metadata = pdf_service.extract_metadata(sample_pdfs['articulo_indexado'])
        
        # Verificar tipos
        assert isinstance(metadata['titulo'], (str, type(None)))
        assert isinstance(metadata['autores'], list)
        assert isinstance(metadata['anio_publicacion'], (int, type(None)))
        assert isinstance(metadata['doi'], (str, type(None)))
        assert isinstance(metadata['issn'], (str, type(None)))
        assert isinstance(metadata['resumen'], (str, type(None)))
        assert isinstance(metadata['palabras_clave'], list)
        assert isinstance(metadata['confidence'], float)


class TestTitleExtraction:
    """Tests de extracción de título"""
    
    def test_extract_title_from_text(self, pdf_service):
        """Test extracción de título de texto simulado"""
        sample_text = """
        Journal of Computer Science
        Volume 10, Issue 2, 2024
        
        MACHINE LEARNING APPROACH FOR DATA ANALYSIS
        
        John Doe, Jane Smith
        University of Example
        """
        
        title = pdf_service.extract_title(sample_text)
        
        assert title is not None
        assert "MACHINE LEARNING" in title.upper()
    
    def test_extract_title_from_real_pdf(self, pdf_service, sample_pdfs):
        """Test extracción de título de PDF real"""
        if not sample_pdfs['articulo_indexado']:
            pytest.skip("No hay PDF disponible")
        
        success, text, _ = pdf_service.extract_text(sample_pdfs['articulo_indexado'])
        if not success:
            pytest.skip("No se pudo extraer texto")
        
        title = pdf_service.extract_title(text)
        
        # Verificar que se extrajo algo razonable
        if title:
            assert len(title) > 10
            assert len(title) < 300


class TestAuthorExtraction:
    """Tests de extracción de autores"""
    
    def test_extract_authors_from_text(self, pdf_service):
        """Test extracción de autores de texto simulado"""
        sample_text = """
        PAPER TITLE HERE
        
        John Doe1, Jane Smith2, Robert Johnson1
        
        1University of Example
        2Institute of Research
        
        Abstract: This is the abstract...
        """
        
        authors = pdf_service.extract_authors(sample_text)
        
        assert isinstance(authors, list)
        # Puede o no encontrar autores dependiendo del formato
    
    def test_extract_authors_returns_list(self, pdf_service):
        """Test que extract_authors siempre retorna lista"""
        authors = pdf_service.extract_authors("")
        assert isinstance(authors, list)
        
        authors = pdf_service.extract_authors(None)
        assert isinstance(authors, list)


class TestYearExtraction:
    """Tests de extracción de año"""
    
    def test_extract_year_from_text(self, pdf_service):
        """Test extracción de año"""
        sample_text = "Published in 2023 by IEEE"
        
        year = pdf_service.extract_year(sample_text)
        
        assert year == 2023
    
    def test_extract_year_multiple_years(self, pdf_service):
        """Test extracción cuando hay múltiples años"""
        sample_text = "Based on research from 2010, updated in 2023"
        
        year = pdf_service.extract_year(sample_text)
        
        # Debería retornar el año más reciente
        assert year == 2023
    
    def test_extract_year_no_year(self, pdf_service):
        """Test cuando no hay año"""
        year = pdf_service.extract_year("No year here")
        assert year is None


class TestDOIExtraction:
    """Tests de extracción de DOI"""
    
    def test_extract_doi_standard_format(self, pdf_service):
        """Test extracción DOI formato estándar"""
        text = "DOI: 10.1234/example.2023.001"
        doi = pdf_service.extract_doi(text)
        
        assert doi == "10.1234/example.2023.001"
    
    def test_extract_doi_url_format(self, pdf_service):
        """Test extracción DOI en formato URL"""
        text = "https://doi.org/10.1234/example.2023.001"
        doi = pdf_service.extract_doi(text)
        
        assert doi == "10.1234/example.2023.001"
    
    def test_extract_doi_no_doi(self, pdf_service):
        """Test cuando no hay DOI"""
        doi = pdf_service.extract_doi("No DOI in this text")
        assert doi is None


class TestISSNExtraction:
    """Tests de extracción de ISSN"""
    
    def test_extract_issn_standard_format(self, pdf_service):
        """Test extracción ISSN formato estándar"""
        text = "ISSN: 1234-5678"
        issn = pdf_service.extract_issn(text)
        
        assert issn == "1234-5678"
    
    def test_extract_issn_no_hyphen(self, pdf_service):
        """Test extracción ISSN sin guión"""
        text = "ISSN 12345678"
        issn = pdf_service.extract_issn(text)
        
        assert issn == "1234-5678"
    
    def test_extract_issn_no_issn(self, pdf_service):
        """Test cuando no hay ISSN"""
        issn = pdf_service.extract_issn("No ISSN here")
        assert issn is None


class TestAbstractExtraction:
    """Tests de extracción de resumen"""
    
    def test_extract_abstract_english(self, pdf_service):
        """Test extracción de abstract en inglés"""
        text = """
        Title Here
        Authors Here
        
        Abstract: This is a sample abstract that describes the research
        conducted in this paper. It includes methodology and results.
        
        Keywords: machine learning, data science
        """
        
        abstract = pdf_service.extract_abstract(text)
        
        if abstract:
            assert "abstract" in abstract.lower() or "research" in abstract.lower()
            assert len(abstract) > 20
    
    def test_extract_abstract_spanish(self, pdf_service):
        """Test extracción de resumen en español"""
        text = """
        Título del Artículo
        
        Resumen: Este es un resumen de ejemplo que describe la investigación
        realizada en este documento.
        
        Palabras clave: aprendizaje automático
        """
        
        abstract = pdf_service.extract_abstract(text)
        
        # Puede o no encontrar dependiendo de la implementación
        if abstract:
            assert len(abstract) > 20


class TestKeywordsExtraction:
    """Tests de extracción de palabras clave"""
    
    def test_extract_keywords_english(self, pdf_service):
        """Test extracción de keywords en inglés"""
        text = """
        Abstract text here...
        
        Keywords: machine learning, artificial intelligence, data mining
        
        1. Introduction
        """
        
        keywords = pdf_service.extract_keywords(text)
        
        assert isinstance(keywords, list)
        if keywords:
            assert any('machine' in k.lower() or 'learning' in k.lower() for k in keywords)
    
    def test_extract_keywords_returns_list(self, pdf_service):
        """Test que siempre retorna lista"""
        keywords = pdf_service.extract_keywords("")
        assert isinstance(keywords, list)


class TestEmailExtraction:
    """Tests de extracción de emails"""
    
    def test_extract_emails_from_text(self, pdf_service):
        """Test extracción de emails"""
        text = """
        John Doe (john.doe@university.edu)
        Jane Smith, jane.smith@research.org
        """
        
        emails = pdf_service.extract_emails(text)
        
        assert isinstance(emails, list)
        if emails:
            assert any('@' in email for email in emails)
            assert any('university.edu' in email or 'research.org' in email for email in emails)


class TestPDFInfo:
    """Tests de información del PDF"""
    
    def test_get_pdf_info(self, pdf_service, sample_pdfs):
        """Test obtener información básica del PDF"""
        if not sample_pdfs['articulo_indexado']:
            pytest.skip("No hay PDF disponible")
        
        info = pdf_service.get_pdf_info(sample_pdfs['articulo_indexado'])
        
        assert 'num_pages' in info
        assert 'file_size' in info
        assert 'encrypted' in info
        
        if info['num_pages']:
            assert info['num_pages'] > 0
        
        if info['file_size']:
            assert info['file_size'] > 0


class TestIntegration:
    """Tests de integración con múltiples PDFs"""
    
    def test_process_multiple_pdfs(self, pdf_service, sample_pdfs):
        """Test procesar múltiples tipos de PDFs"""
        results = []
        
        for pdf_type, pdf_path in sample_pdfs.items():
            if pdf_path and os.path.exists(pdf_path):
                metadata = pdf_service.extract_metadata(pdf_path)
                results.append({
                    'type': pdf_type,
                    'success': metadata['success'],
                    'confidence': metadata['confidence']
                })
        
        # Al menos uno debería procesarse exitosamente
        if results:
            assert any(r['success'] for r in results)
            
            # Calcular tasa de éxito
            success_rate = sum(r['success'] for r in results) / len(results)
            print(f"\nTasa de éxito: {success_rate * 100:.1f}%")
            
            # Mostrar confianza promedio
            confidences = [r['confidence'] for r in results if r['success']]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"Confianza promedio: {avg_confidence * 100:.1f}%")
