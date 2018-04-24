import os

from inifile import IniFile
from lektor.context import get_ctx, url_to
from lektor.pluginsystem import Plugin
from markupsafe import Markup, escape

__version__ = '1'


class OpenGraph(Plugin):
    name = 'Open Graph'
    description = 'Add Open Graph tags to Lektor pages.'

    def on_setup_env(self, **kwargs):
        self.env.jinja_env.globals['open_graph'] = self

    def get_og_items(self, record):
        plugin_config = self.get_config()
        model_config = IniFile(record.datamodel.filename)
        root = get_ctx().pad.root
        items = {
            'site_name': plugin_config.get(
                'global.site_name', self.env.project.name),
            'url': url_to(record, external=True),
            'title': get_og_title(record, model_config, root),
        }
        image = get_og_image(record, root)

        if image is not None:
            items.update({
                'image': url_to(image, external=True),
                'image:width': image.width,
                'image:height': image.height,
                'image:type': 'image/' + image.format,
            })

            if image.parent is root:
                items['image:alt'] = 'logo'

        return items

    def render_tags(self, record):
        out = []

        for key, value in self.get_og_items(record).items():
            if not value:
                continue

            out.append(u'<meta property="og:{}" content="{}">'.format(
                key, escape(value)))

        return Markup('\n'.join(out))


def get_og_title(record, model_config, root):
    mc_field = model_config.get('plugin.open-graph.title_field')

    if mc_field in record:
        return record[mc_field]

    if 'og_title' in record:
        return record['og_title']

    if record is not root:
        return record.record_label


def get_og_image(record, root):
    image = record.attachments.images.filter(is_og_image).first()

    if image is not None:
        return image

    image = root.attachments.images.filter(is_og_image).first()

    if image is not None:
        return image


def is_og_image(attachment):
    return os.path.splitext(attachment['_id'].lower())[0] == 'og_image'
