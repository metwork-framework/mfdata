{% block main -%}
#!/usr/bin/env {{cookiecutter.python_version|default('python3')}}

from acquisition import Acquisition{{typeStep}}Step


class {{cookiecutter.name|capitalize}}{{typeStep}}MainStep(
        Acquisition{{typeStep}}Step):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "main"

{% block process %}
{% endblock %}


if __name__ == "__main__":
    x = {{cookiecutter.name|capitalize}}{{typeStep}}MainStep()
    x.run()
{% endblock %}
