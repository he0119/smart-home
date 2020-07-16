# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/he0119/smart-home/compare/v0.3.1...HEAD

[0.3.1]: https://github.com/he0119/smart-home/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/he0119/smart-home/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/he0119/smart-home/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/he0119/smart-home/releases/tag/v0.1.0
