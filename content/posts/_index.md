---
cascade:
  # - _target:
  #     development: development
  #   build:
  #     render: always
  #     list: always
  - _target:
      environment: production
  # 支持list
    build:
      list: never
      publishResources: true
      render: never
    params:
---