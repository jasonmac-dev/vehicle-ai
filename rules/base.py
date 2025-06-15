class RuleBase:
    id = ""
    name = ""
    description = ""
    category = ""
    type = "ai"  # or 'manual', 'openai'

    def check(self, image, image_bytes=None):
        raise NotImplementedError 