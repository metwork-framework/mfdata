{% block main -%}
#!/usr/bin/env python

from acquisition import Acquisition{{typeStep}}Step


class {{cookiecutter.name|capitalize}}{{typeStep}}MainStep(
        Acquisition{{typeStep}}Step):

    step_name = "main"

{% block process %}
{% endblock %}


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}{{typeStep}}MainStep()
    x.run()
{% endblock %}
