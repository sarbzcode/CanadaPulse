{% macro generate_schema_name(custom_schema_name, node) -%}
  {{ env_var('DBT_SCHEMA_PREFIX', '') ~ (custom_schema_name | trim if custom_schema_name else target.schema) }}
{%- endmacro %}
