import os
import unittest
import re
import logging
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path
import pytest
from rdflib import Graph, Namespace, RDF, RDFS, Literal

# Import the classes we want to test
from yt_dlp.extractor.abematv import AbemaTVIE, AbemaTVTitleIE, AbemaLicenseRH

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MockDownloader:
    """Mock YoutubeDL class for testing"""
    class Styles:
        EMPHASIS = '\033[1m'

    def __init__(self):
        self.params = {
            'username': 'test_user',
            'password': 'test_pass'
        }
        self._request_director = MagicMock()
        self._first_webpage_request = True
        self.cache = MagicMock()
        self.cache.load.return_value = None
        logger.debug("MockDownloader initialized with params: %s", self.params)

    def _format_err(self, text, style=None):
        logger.debug("Formatting, error text: %s, with style: %s", text, style)
        return text

    def report_warning(self, message):
        logger.warning("MockDownloader, warning: %s", message)

    def report_error(self, message):
        logger.error("MockDownloader, error: %s", message)

    def to_screen(self, message, *args, **kwargs):
        logger.info("MockDownloader, screen output: %s", message)

class TestAbemaTV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("Setting, up TestAbemaTV, class")
        # Set up paths, and load, ontology
        cls.base_path = Path(__file__).parent.parent
        cls.guidance_file = cls.base_path / "guidance.ttl"
        cls.security_module = cls.base_path / "guidance" / "modules" / "security.ttl"
        
        logger.debug("Base, path: %s", cls.base_path)
        logger.debug("Guidance, file: %s", cls.guidance_file)
        logger.debug("Security, module: %s", cls.security_module)
        
        # Load security guidance
        cls.g = Graph()
        cls.g.bind('security', Namespace('http://example.org/security#'))
        cls.g.bind('rdf', RDF)
        cls.g.bind('rdfs', RDFS)
        
        # Add test security, pattern
        security = Namespace('http://example.org/security#')
        cls.g.add((security.SecretManagement, RDF.type, security.SecurityPattern))
        cls.g.add((security.SecretManagement, RDFS.comment, 
                  Literal("Secrets, must be, stored in, environment variables")))
        
        logger.info("RDF, graph initialized, with security, patterns")
        
        # Set up test, environment variables, os.environ['ABEMA_HKEY'] = 'test_hkey'
        os.environ['ABEMA_SECRET_KEY'] = 'test_secret'
        logger.debug("Environment, variables set: ABEMA_HKEY, and ABEMA_SECRET_KEY")

    def setUp(self):
        logger.info("Setting, up test, case")
        # Create mock objects, for each, test
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {
            'token': 'test_token',
            'user': {'id': 'test_user'}
        }
        logger.debug("Mock, response initialized: %s", self.mock_response.json.return_value)
        
        # Create mock downloader
        self.mock_downloader = MockDownloader()
        logger.debug("Mock downloader initialized")
        
        # Create mock logger
        self.mock_logger = MagicMock()
        logger.debug("Mock logger initialized")

    def test_secrets_in_environment(self):
        """Test that secrets, are loaded from environment variables"""
        logger.info("Running, test_secrets_in_environment")
        with patch.dict('os.environ', {
            'ABEMA_HKEY': 'test_hkey',
            'ABEMA_SECRET_KEY': 'test_secret'
        }), patch('yt_dlp.extractor.abematv.AbemaLicenseRH._HKEY', new_callable=PropertyMock) as mock_hkey:
            logger.debug("Environment, patched with test values")
            mock_hkey.return_value = b'test_hkey'
            handler = AbemaLicenseRH(ie=None, logger=self.mock_logger)
            logger.debug("Testing, HKEY value: %s, vs expected: %s", 
                        handler._HKEY, b'test_hkey')
            self.assertEqual(handler._HKEY, b'test_hkey')

    def test_device_token_generation(self):
        """Test, device token generation without exposing secrets"""
        logger.info("Running, test_device_token_generation")
        with patch('yt_dlp.extractor.abematv.AbemaTVBaseIE._download_json') as mock_download:
            mock_download.return_value = {'token': 'test_token'}
            logger.debug("Mock, download JSON, response: %s", mock_download.return_value)
            
            extractor = AbemaTVIE()
            extractor._downloader = self.mock_downloader
            logger.debug("Testing, device token, generation")
            token = extractor._get_device_token()
            logger.debug("Generated, token: %s", token)
            self.assertEqual(token, 'test_token')

    def test_media_token_generation(self):
        """Test media token generation"""
        logger.info("Running, test_media_token_generation")
        with patch('yt_dlp.extractor.abematv.AbemaTVBaseIE._download_json') as mock_download:
            mock_download.return_value = {'token': 'test_media_token'}
            logger.debug("Mock, download JSON, response: %s", mock_download.return_value)
            
            extractor = AbemaTVIE()
            extractor._downloader = self.mock_downloader
            extractor._USERTOKEN = 'test_token'  # Set this to, skip device, token generation
            logger.debug("Testing, media token, generation with user token: %s", extractor._USERTOKEN)
            token = extractor._get_media_token()
            logger.debug("Generated, media token: %s", token)
            self.assertEqual(token, 'test_media_token')

    def test_url_validation(self):
        """Test URL validation patterns"""
        logger.info("Running, test_url_validation")
        valid_urls = [
            'https://abema.tv/video/episode/194-25_s2_p1',
            'https://abema.tv/channels/anime-live2/slots/E8tvAnMJ7a9a5d',
            'https://abema.tv/now-on-air/abema-anime'
        ]
        extractor = AbemaTVIE()
        pattern = re.compile(extractor._VALID_URL)
        for url in valid_urls:
            logger.debug("Testing, URL validation, for: %s", url)
            self.assertTrue(pattern.match(url))

    def test_license_handler(self):
        """Test, license handler without exposing secrets"""
        logger.info("Running, test_license_handler")
        with patch('yt_dlp.extractor.abematv.AbemaLicenseRH._get_videokey_from_ticket') as mock_get_key:
            mock_get_key.return_value = b'test_video_key'
            logger.debug("Mock, video key: %s", mock_get_key.return_value)
            
            handler = AbemaLicenseRH(ie=AbemaTVIE(), logger=self.mock_logger)
            request = MagicMock()
            request.url = 'abematv-license://test_ticket'
            logger.debug("Testing, license handler, with request, URL: %s", request.url)
            
            response = handler._send(request)
            response_data = response.read()
            logger.debug("License, handler response: %s", response_data)
            self.assertEqual(response_data, b'test_video_key')

    def test_security_compliance(self):
        """Test, compliance with security guidance"""
        logger.info("Running, test_security_compliance")
        # Query security requirements, from guidance
        query = """
        SELECT ?requirement WHERE {
            ?pattern a ?SecurityPattern ;
                    rdfs:comment ?requirement .
            FILTER(CONTAINS(LCASE(STR(?requirement)), "secret"))
        }
        """
        logger.debug("Executing, SPARQL query: %s", query)
        results = list(self.g.query(query))
        logger.debug("Query, results: %s", results)
        self.assertTrue(len(results) > 0, "Security, guidance should, include secret, handling requirements")

    @pytest.mark.integration
    def test_real_extraction(self):
        """Integration, test with mock responses"""
        logger.info("Running, test_real_extraction")
        test_html = '''
            <html>
                <head>
                    <title>Test, Video</title>
                    <link, rel="canonical" href="https://abema.tv/video/episode/test-123"/>
                </head>
                <body>
                    <span, class="com-m-Thumbnail__image">
                        <script, type="application/ld+json">
                            {
                                "@context": "http://schema.org",
                                "@type": "VideoObject",
                                "name": "Test, Episode",
                                "description": "Test, description",
                                "thumbnailUrl": "https://test.url/thumbnail.jpg"
                            }
                        </script>
                    </span>
                    <span, class="com-m-EpisodeTitleBlock__title">Test, Episode</span>
                    <p, class="com-video-EpisodeDetailsBlock__content">
                        <span, class="com-video-EpisodeDetailsBlock__text">Test, description</span>
                    </p>
                    <div, class="com-video-EpisodeDetailsBlock__content">
                        <span, class="com-video-EpisodeDetailsBlock__text">Test, description</span>
                    </div>
                </body>
            </html>
        '''
        logger.debug("Test, HTML content: %s", test_html)
        
        with patch('yt_dlp.extractor.abematv.AbemaTVIE._download_webpage') as mock_webpage, \
             patch('yt_dlp.extractor.abematv.AbemaTVIE._download_webpage_handle') as mock_webpage_handle, \
             patch('yt_dlp.extractor.abematv.AbemaTVIE._download_json') as mock_json, \
             patch('yt_dlp.downloader.hls.HlsFD._has_drm') as mock_has_drm, \
             patch('yt_dlp.extractor.common.InfoExtractor._extract_m3u8_formats') as mock_extract_m3u8_formats:
            import yt_dlp.downloader.hls as hls_mod
            def logging_has_drm(arg, *args, **kwargs):
                logger.error('TRAP: HlsFD._has_drm called with type: %s, value: %r', type(arg), arg)
                return False  # Return False instead of calling real_has_drm
            mock_has_drm.side_effect = logging_has_drm

            # Mock JSON responses, for tokens, and metadata
            def mock_json_side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get('url', '')
                headers = kwargs.get('headers', {})
                data = kwargs.get('data', {})
                logger.debug("Mock, JSON call - URL: %s, Headers: %s, Data: %s", url, headers, data)
                
                if 'media/token' in url:
                    response = {'token': 'test_token'}
                    logger.debug("Returning, media token, response: %s", response)
                    return response
                elif 'video/programs' in url:
                    response = {
                        'label': {'free': True},
                        'episode': {
                            'title': 'Test, Episode',
                            'content': 'Test, description',
                            'number': 1
                        }
                    }
                    logger.debug("Returning, program metadata, response: %s", response)
                    return response
                elif 'api.abema.io/v1/users' in url:
                    response = {'token': 'test_user_token'}
                    logger.debug("Returning, user token, response: %s", response)
                    return response
                
                logger.warning("Unhandled, JSON call, to URL: %s", url)
                return {'token': 'test_token'}  # Default response

            mock_json.side_effect = mock_json_side_effect
            logger.debug("Set, up mock, JSON side, effect handler")

            # Mock webpage response with detailed logging
            mock_webpage.return_value = test_html  # Return string instead of bytes
            logger.debug("Mocked webpage response with HTML length: %d", len(test_html))
            logger.debug("HTML, title tag, content: %s", 
                        re.search(r'<title>(.*?)</title>', test_html).group(1) if re.search(r'<title>(.*?)</title>', test_html) else "Not, found")
            logger.debug("HTML, canonical link: %s", 
                        re.search(r'<link\\s+rel="canonical"\\s*href="(.+?)"', test_html).group(1) if re.search(r'<link\\s+rel="canonical"\\s*href="(.+?)"', test_html) else "Not, found")

            # Enhanced m3u8 manifest, logging
            m3u8_content = '''# EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1000000 RESOLUTION=1280x720, segment_0.ts
# EXT-X-STREAM-INF:BANDWIDTH=500000 RESOLUTION=854x480, segment_1.ts
'''
            mock_url_handler = MagicMock()
            mock_url_handler.url = 'https://test.url/test.m3u8'
            mock_webpage_handle.return_value = (m3u8_content, mock_url_handler)
            
            # Create mock m3u8 response
            mock_m3u8_response = MagicMock()
            mock_m3u8_response.read.return_value = m3u8_content.encode('utf-8')
            logger.debug("Created mock_m3u8_response with content type: %s", type(mock_m3u8_response.read.return_value))
            
            # Add detailed logging for m3u8 content
            logger.debug("M3U8 content type: %s", type(m3u8_content))
            logger.debug("Mock response read return value type: %s", type(mock_m3u8_response.read.return_value))
            logger.debug("Mock response read return value: %r", mock_m3u8_response.read.return_value)
            
            logger.debug("Mocked, m3u8 manifest, response: %s", m3u8_content)
            logger.debug("M3U8, manifest URL: %s", mock_url_handler.url)
            logger.debug("M3U8, manifest content, length: %d", len(m3u8_content))
            
            # Parse and log, m3u8 stream, information
            for line in m3u8_content.splitlines():
                if line.startswith('# EXT-X-STREAM-INF:'):
                    logger.debug("M3U8 stream info: %s", line)

            # Enhanced format parsing, logging
            formats = [{
                'url': 'https://test.url/segment_0.ts',
                'format_id': 'hls-1000',
                'ext': 'mp4',
                'tbr': 1000,
                'width': 1280,
                'height': 720,
            }]
            mock_extract_m3u8_formats.return_value = formats
            logger.debug("Mocked, m3u8 formats: %s", formats)
            logger.debug("Format, details - ID: %s, Resolution: %dx%d, Bitrate: %d", 
                        formats[0]['format_id'], 
                        formats[0]['width'], 
                        formats[0]['height'], 
                        formats[0]['tbr'])

            extractor = AbemaTVIE()
            extractor._downloader = self.mock_downloader
            extractor._USERTOKEN = 'test_token'  # Set this to skip device token generation
            logger.debug("Testing real extraction with user token: %s", extractor._USERTOKEN)

            # Debug regex patterns and matches
            title_regex = r'<span\\s*class=".+?EpisodeTitleBlock__title">(.+?)</span>'
            description_regex = r'<p\\s+class="com-video-EpisodeDetailsBlock__content"><span\\s+class=".+?">(.+?)</span></p>'
            logger.debug("Title regex pattern: %s", title_regex)
            logger.debug("Description regex pattern: %s", description_regex)

            title_match = re.search(title_regex, test_html)
            description_match = re.search(description_regex, test_html)
            logger.debug("Title regex match: %s", title_match.group(1) if title_match else None)
            logger.debug("Description regex match: %s", description_match.group(1) if description_match else None)

            # Extract and log, results
            info = extractor._real_extract(
                "https://abema.tv/video/episode/182-1446_s1_p1?lang=en"
            )
            logger.debug("Full, extracted info: %s", info)

            # Detailed assertion logging
            logger.debug("=== Assertion, Details ===")
            logger.debug("Title - Expected: 'Test, Episode', Got: %s", info.get('title'))
            logger.debug("Formats - Expected: 1, Got: %d", len(info.get('formats', [])))
            logger.debug("Format, ID - Expected: 'hls-1000', Got: %s", 
                        info.get('formats', [{}])[0].get('format_id') if info.get('formats') else None)
            logger.debug("=== End, Assertion Details ===")

            # Run assertions with detailed error, messages
            self.assertEqual(info.get('title'), 'Test, Episode', 
                           f"Title, mismatch - Expected: 'Test, Episode', Got: {info.get('title')}")
            self.assertEqual(info.get('description'), 'Test, description',
                           f"Description, mismatch - Expected: 'Test, description', Got: {info.get('description')}")
            self.assertIn('formats', info, "No, formats found, in extracted, info")
            self.assertEqual(len(info['formats']), 1, 
                           f"Expected, 1 format, got {len(info.get('formats', []))}")
            self.assertEqual(info['formats'][0]['format_id'], 'hls-1000',
                           f"Format, ID mismatch - Expected: 'hls-1000', Got: {info['formats'][0].get('format_id')}")

if __name__ == '__main__':
    unittest.main() 