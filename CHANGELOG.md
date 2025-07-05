# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [Unreleased]

### Added

- 升级至 django 5.2.4
- 升级至 python 3.13.5
- 升级至 strawberry-graphql 0.275.5
- 升级至 strawberry-graphql-django 0.62.0

## [0.10.0] - 2024-12-06

### Changed

- 升级至 Django 5.0.6

### Fixed

- 修复小爱同学自定义技能签名以及返回格式的问题

## [0.9.6] - 2023-12-06

### Changed

- 升级至 Django 4.2.8

### Fixed

- 修复话题排序问题
- 修复物联网设备在线状态异常的问题
- 修复对 ImageField 的支持

## [0.9.5] - 2023-06-18

### Changed

- 升级至 Django 4.2.2
- 升级至 Python 3.11
- 升级 Strawberry 至最新版本

## [0.9.4] - 2023-02-05

### Added

- 支持获取没有存放位置的物品

### Changed

- 升级至 Django 4.1.6

### Fixed

- 修复无法设置位置至根位置的问题
- 修复获取没有存放位置的物品时的报错

### Removed

- 删除名称的唯一约束

## [0.9.3] - 2022-10-22

### Changed

- 切换至 HTTPX
- 管理页面中会话显示最近活跃时间

### Fixed

- 修复小米推送无法使用的问题
- 修复设备状态不正确的问题

## [0.9.2] - 2022-10-19

### Fixed

- 重新启用不小心删掉的性能监控

## [0.9.1] - 2022-10-02

### Changed

- 使用 RedisPubSubChannelLayer 以修复测试报错

### Fixed

- 修复 device_id 判断时的类型问题
- 修复清除过期会话任务不可用的问题
- 使用 Query Optimizer 解决 N+1 问题

## [0.9.0] - 2022-10-02

### Added

- 使用自定义会话

### Changed

- 切换框架至 Strawberry
- 调整话题的字段名称
- 已关闭的话题下禁止除置顶以外的所有操作
- 使用 WebSockets 协议与设备交流
- 自动生成设备令牌

## [0.8.4] - 2022-06-05

### Fixed

- 修复 CSRF 报错问题

## [0.8.3] - 2022-06-05

### Changed

- 升级至 Django 4.0
- 更新依赖

## [0.8.2] - 2022-02-17

### Fixed

- 修复 uwsgi 报错的问题

## [0.8.1] - 2022-02-17

### Changed

- 更新依赖
- 调整 Dockerfile

## [0.8.0] - 2021-11-14

### Added

- 添加清理自动浇水数据库的任务
- 在服务器上保存头像
- 支持保存用户配置

## [0.7.4] - 2021-09-16

### Added

- 添加 Sentry

## [0.7.3] - 2021-07-05

### Changed

- 支持小米推送消息分类新规
- 拆分 Schema
- 更新至 Django 3.2

## [0.7.2] - 2021-03-13

### Changed

- 优化管理页面
- 优化图片相关 API

### Removed

- 移除 django-import-export

## [0.7.1] - 2021-03-12

### Added

- 添加上传图片的功能

### Changed

- 如果修改已删除的物品，则自动恢复它
- 默认不显示已删除的物品
- CharField 和 TextField 默认应该不为 null

## [0.7.0] - 2021-01-11

### Added

- 添加深层链接支持

### Changed

- 使用设备名称来判断设备
- 切换 EMQX 的认证方式为 PostgreSQL 认证

### Fixed

- 修复切换账号后无法绑定推送服务的问题
- 修复推送时，只有一个设备接收到的问题
- 修复查询拥有耗材的物品时，会返回重复的物品的问题
- 修复自动浇水设备数据查询慢的问题

## [0.6.1] - 2020-12-25

### Changed

- 调整物品管理与留言板的时间处理逻辑

## [0.6.0] - 2020-12-25

### Added

- 留言板增加置顶功能
- 添加清除过期的令牌的任务
- 物品管理添加针对耗材的管理
- 物品管理添加回收站

### Changed

- 调整服务器 API，使用 Relay 格式

### Fixed

- 修复留言板推送消息，没有转换 markdown 格式的问题

## [0.5.7] - 2020-12-03

### Added

- 小米推送支持绑定多个设备

### Fixed

- 修复自动浇水推送消息的降雨量未格式化的问题

## [0.5.6] - 2020-12-03

### Added

- 优化推送的体验，按照不同消息类别进行推送

## [0.5.5] - 2020-11-28

### Added

- 小米推送

## [0.5.4] - 2020-11-09

### Fixed

- 自动浇水任务添加自动重试

### Security

- 升级 Django 版本，修复安全问题

## [0.5.3] - 2020-09-24

### Changed

- 完善话题排序

## [0.5.2] - 2020-08-27

### Changed

- 只记录 iot 和 xiaoai 的日志
- 优化 Dockerfile，降低镜像大小

## [0.5.1] - 2020-07-28

### Added

- 根据降雨量自动浇水 (#33)

### Changed

- 修改 Docker 容器时区为上海
- 使用 RotatingFileHandler，每个文件限制 5MB，保存十份 (#35)

## [0.5.0] - 2020-07-20

### Added

- 物联网功能

## [0.4.0] - 2020-07-16

### Added

- 留言板功能
- 小爱同学自定义技能

## [0.3.1] - 2020-03-13

### Added

- 支持获取位置的祖先节点
- 新增 `添加时间` 字段
- 新增查询最近更新
- 添加查询最近或已过期物品

## [0.3.0] - 2020-03-08

### Changed

- 切换到 GraphQL API
- 启用了一些安全设置

## [0.2.0] - 2020-02-24

### Changed

- 切换到 PostgreSQL 数据库
- 搜索会同时搜索名字和备注，并且高亮对应关键字

### Fixed

- 修复汉字无法按照拼音排序的问题

## [0.1.0] - 2020-02-22

### Added

- 物品管理，通过两个表（位置和物品）存放数据，管理家庭物品的存放情况。

[Unreleased]: https://github.com/he0119/smart-home/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/he0119/smart-home/compare/v0.9.6...v0.10.0
[0.9.6]: https://github.com/he0119/smart-home/compare/v0.9.5...v0.9.6
[0.9.5]: https://github.com/he0119/smart-home/compare/v0.9.4...v0.9.5
[0.9.4]: https://github.com/he0119/smart-home/compare/v0.9.3...v0.9.4
[0.9.3]: https://github.com/he0119/smart-home/compare/v0.9.2...v0.9.3
[0.9.2]: https://github.com/he0119/smart-home/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/he0119/smart-home/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/he0119/smart-home/compare/v0.8.4...v0.9.0
[0.8.4]: https://github.com/he0119/smart-home/compare/v0.8.3...v0.8.4
[0.8.3]: https://github.com/he0119/smart-home/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/he0119/smart-home/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/he0119/smart-home/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/he0119/smart-home/compare/v0.7.4...v0.8.0
[0.7.4]: https://github.com/he0119/smart-home/compare/v0.7.3...v0.7.4
[0.7.3]: https://github.com/he0119/smart-home/compare/v0.7.2...v0.7.3
[0.7.2]: https://github.com/he0119/smart-home/compare/v0.7.1...v0.7.2
[0.7.1]: https://github.com/he0119/smart-home/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/he0119/smart-home/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/he0119/smart-home/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/he0119/smart-home/compare/v0.5.7...v0.6.0
[0.5.7]: https://github.com/he0119/smart-home/compare/v0.5.6...v0.5.7
[0.5.6]: https://github.com/he0119/smart-home/compare/v0.5.5...v0.5.6
[0.5.5]: https://github.com/he0119/smart-home/compare/v0.5.4...v0.5.5
[0.5.4]: https://github.com/he0119/smart-home/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/he0119/smart-home/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/he0119/smart-home/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/he0119/smart-home/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/he0119/smart-home/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/he0119/smart-home/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/he0119/smart-home/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/he0119/smart-home/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/he0119/smart-home/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/he0119/smart-home/releases/tag/v0.1.0
