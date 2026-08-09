# HomeAssistant Service Entities integration

![Version](https://img.shields.io/github/v/release/RoboMagus/home-assistant-service-entities?style=for-the-badge)
![License](https://img.shields.io/github/license/RoboMagus/home-assistant-service-entities?style=for-the-badge)

## ⚠️ Work In Progress

This is very much a Work In Progress custom integration!

Do not use if you aren't ok with things breaking.

## About

This custom integration provides a way of creating and updating sensor entities by calling a service from HA scripts and automations. Usefull for e.g. creating separate sensors based on Webhook notifications.

## Features

- `service_entities.set_entity` service:
  - Create sensors with user specified `entity_id`, `name`, `icon`, and `unit_of_measurement`.
  - Update sensor `state` and `attributes`.
- `service_entities.delete_entity` service:
  - Delete created sensors.
- Sensors persist across reboots.
- Sensors can be custommized through frontend as they are properly registered using `unique_id`s.

## Installation

Install this component by clicking the button or following the manual instructions below:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RoboMagus&repository=home-assistant-service-entities&category=integration)

Follow [this guide](https://www.hacs.xyz/docs/faq/custom_repositories/) for installing custom repositories using HACS. For the URL of the repository use `https://github.com/RoboMagus/home-assistant-service-entities` and for type select `Integration`.


