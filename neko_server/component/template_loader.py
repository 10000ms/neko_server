import os


class TemplateLoader:
    """
    模板文件加载器
    """

    def __init__(self, path, encoding='utf-8'):
        self.path = path
        self.encoding = encoding

    @staticmethod
    def split_template_path(template):
        return template.split('/')

    def get_source(self, template):
        pieces = self.split_template_path(template)
        file_path = os.path.join(self.path, *pieces)
        f = os.path.isfile(file_path)
        if f is not None:
            with open(file_path, encoding=self.encoding) as f:
                contents = f.read()
                return contents
        else:
            raise IOError('模板文件不存在：<{}>'.format(template))
