{% extends "_common/main.py" %}

{% set typeStep = "" %}

{% block process %}

    def process(self, xaf):
        self.info("process for file %s" % xaf.filepath)
        return True


{% endblock %}
