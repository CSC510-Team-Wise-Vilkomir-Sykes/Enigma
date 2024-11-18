import unittest
from unittest.mock import patch, Mock
from src.scraper import get_chart_links

class TestScraper(unittest.TestCase):

    @patch('src.scraper.requests.get')
    def test_get_chart_links_is_list(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a href="/charts/hot-100"></a>
                </div>
                <div class="o-chart-list-card">
                    <a href="/charts/billboard-200"></a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertIsInstance(chart_links, list)

    @patch('src.scraper.requests.get')
    def test_get_chart_links_contains_hot_100(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a href="/charts/hot-100"></a>
                </div>
                <div class="o-chart-list-card">
                    <a href="/charts/billboard-200"></a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertIn('hot-100', chart_links)

    @patch('src.scraper.requests.get')
    def test_get_chart_links_contains_billboard_200(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a href="/charts/hot-100"></a>
                </div>
                <div class="o-chart-list-card">
                    <a href="/charts/billboard-200"></a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertIn('billboard-200', chart_links)

    @patch('src.scraper.requests.get')
    def test_get_chart_links_empty(self, mock_get):
        sample_html = '''
        <html>
            <body>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, [])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_no_links(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                </div>
                <div class="o-chart-list-card">
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, [])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_invalid_html(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="invalid-class">
                    <a href="/charts/hot-100"></a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, [])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_partial_links(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a href="/charts/hot-100"></a>
                </div>
                <div class="o-chart-list-card">
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, ['hot-100'])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_malformed_html(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a href="/charts/hot-100"></a>
                </div>
                <div class="o-chart-list-card">
                    < href="/charts/billboard-200">
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, ['hot-100'])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_no_href(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a></a>
                </div>
                <div class="o-chart-list-card">
                    <a></a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, [])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_multiple_links(self, mock_get):
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                    <a href="/charts/hot-100"></a>
                </div>
                <div class="o-chart-list-card">
                    <a href="/charts/billboard-200"></a>
                </div>
                <div class="o-chart-list-card">
                    <a href="/charts/rock-songs"></a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, ['hot-100', 'billboard-200', 'rock-songs'])

    @patch('src.scraper.requests.get')
    def test_get_chart_links_sample_chart(self, mock_get):
        """Test that get_chart_links correctly parses links from sample_chart.html."""
        with open('data/sample_charts.html', 'r') as file:
            sample_html = file.read()
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertIn('hot-100', chart_links)
        self.assertIn('billboard-200', chart_links)

    @patch('src.scraper.requests.get')
    def test_get_chart_links_sample_chart_no_links(self, mock_get):
        """Test that get_chart_links returns an empty list when sample_chart.html has no valid links."""
        sample_html = '''
        <html>
            <body>
                <div class="o-chart-list-card">
                </div>
                <div class="o-chart-list-card">
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = Mock(status_code=200, content=sample_html)
        chart_links = get_chart_links()
        self.assertEqual(chart_links, [])

if __name__ == '__main__':
    unittest.main()
