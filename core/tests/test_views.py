from django.core.urlresolvers import reverse

from .utils import UserBaseTestCase


class SimpleViewsTestCase(UserBaseTestCase):

    def test_renders_main_view(self):
        with self.assertTemplateUsed('core/index.html'):
            response = self.client.get(reverse('main'))

        self.assertEqual(200, response.status_code)
