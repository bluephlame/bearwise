{{text}} - {{id}}
{% if note is defined and note %} 
### NOTE 
{{note}}
{% endif %}
{% for tag in tags %} #{{tag}} {% endfor %}


