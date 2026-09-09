{% macro stable_key(fields) -%}
md5(jsonb_build_array({{ fields | join(', ') }})::text)
{%- endmacro %}
