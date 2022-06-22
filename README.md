# Lakat. Lords and Knights automation tool

Online game website: https://lordsandknights.com  
Lakat is a simple tool to automate your daily routine job in a game.  
Tested on MacOS with python version 3.8.10.

## Features

* Multiple accounts supported.
* Building upgrade.
* Research. Start first available research in habitat's research building.
* Use mass functions to send troops to missions in case habitats are not under attack.
* Use mass functions to exchange resources to silver using Ox cart units.

## Disclaimer

USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR RESULTS.  
Your game account may be blocked or banned by bot detection systems.

## Configuration

Make sure you have `config.yml` file in application's root directory.  
There is `config.sample.yml` file provided as an example.

* **interval**: `number` (required) – interval between bot runs, in minutes
* **profiles_path**: `string` (optional, `profiles` by default) – path to save browser profile(faster subsequent logins)
* **headless**: `boolean` (optional, `true` by default) – browser mode, make sure param value is `true` in dockerized usage
* **debug**: `boolean` (optional, `false` by default) – enables debug mode, if param value is `true` screenshot of current page will be captured and saved on runtime errors
* **screenshots_path**: `string` (optional, `screenshots` by default) – path to save screenshots if debug mode is enabled.

### Account configuration

* **email**: `string` (required) – account email
* **password**: `string` (required) – account password
* **world**: `string` (required) – world alias
* **missions**: `boolean` (required) – if param value is `true` troops will be send to missions on each bot run. If at least one habitat is under attack param is ignored
* **silver\_barter\_threshold**: `number` (required) – expected amount of silver to start exchange resources from all castles to silver.
* **\<habitat_type\>.upgrades** – habitat(`castle`|`fortress`|`city`) building upgrade steps

## Usage

Clone the repo - `git clone https://github.com/arskode/lakat && cd lakat`  
Make sure you have `config.yml` file in application's root directory.

### Dockerized

_This is the recommended way to run Lakat. Make sure **headless** config param value is `true`_

* build and run - `docker compose build && docker compose up`

### Directly

* activate python venv the way you prefer; this step is optional but recommended 
* install dependencies - `make install`
* run - `make run`

