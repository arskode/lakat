import logging
from dataclasses import dataclass
from typing import Dict, Generator, List

from playwright.sync_api import BrowserContext, Locator, TimeoutError

from lakat.config import AccountConfig, Building
from lakat.constants import (
    HABITAT_TYPE_MAP,
    LEVEL_COMPILED,
    SECOND,
    SERVER_URL,
    HabitatType,
    ResearchBuilding,
)


@dataclass
class ParsedBuilding:
    name: str
    level: int
    upgrade_button: Locator


class Lakat:
    def __init__(
        self, config: AccountConfig, context: BrowserContext, logger: logging.Logger
    ) -> None:
        self.config = config
        self.context = context
        self.page = self.context.new_page()
        self.active_habitat_name = ""
        self.active_habitat_type = ""
        self.logger = logger

    def login(self) -> None:
        self.page.goto(SERVER_URL)

        try:
            selector = ".form--data--logout"
            logout = self.page.wait_for_selector(selector, timeout=5 * SECOND, state="attached")
            if logout:
                logout.click()
        except TimeoutError:
            pass

        self.page.locator('[placeholder="Email"]').fill(self.config.email)
        self.page.locator('[placeholder="Password"]').fill(self.config.password)
        self.page.locator('button:has-text("Log in")').click()
        self.page.locator(f"text={self.config.world}").click()

        # just to be sure page loaded completely
        selector = "//div[contains(@class, 'icon-bar-buildings')]"
        self.page.wait_for_selector(selector, state="attached")
        self.page.wait_for_selector("//div[@id='over-layer--game-loading']", state="detached")

        self.log(f"logged in as {self.config.email}", habitat_name=False)

    def close_popup(self) -> None:
        selectors = (
            "#game-pop-up-layer .event-pop-up-button.ButtonRedAccept",
            "#game-pop-up-layer .event-pop-up-button.Back",
        )
        for selector in selectors:
            try:
                popup = self.page.wait_for_selector(selector, timeout=2 * SECOND, state="attached")
                if popup:
                    popup.click()
                    self.log("popup closed", habitat_name=False)
                    return self.close_popup()  # same popup can appear again
            except TimeoutError:
                pass

    def update_active_habitat_name(self) -> None:
        locators = self.page.locator(".habitat-chooser .habitat-chooser--title span")
        name = locators.first.text_content()
        if not name:
            raise Exception("couldn't get habitat name")

        self.active_habitat_name = name.strip()

    def click_building_list(self) -> None:
        self.page.locator("div.button-for-bars.top-bar-button--HabitatBuildings").click()

    def click_mass_functions_button(self) -> None:
        self.page.locator(".icon.icon-game.white.icon-general-functions").click()

    def update_habitat_type(self) -> None:
        """
        Ore store building name is used to get habitat type
        """

        selector = (
            "(//div[contains(@class, 'with-icon-left with-icon-right')]//"
            "div[contains(@class, 'text-name-with-emo-icons')])[last()]"
        )
        name = self.page.locator(selector).inner_text()
        self.active_habitat_type = HABITAT_TYPE_MAP[name]

    @staticmethod
    def iter_locator(locator: Locator) -> Generator[Locator, None, None]:
        for i in range(locator.count()):
            yield locator.nth(i)

    def upgradable_buildings(self) -> Dict[str, ParsedBuilding]:
        upgradable_buildings = {}
        buildings_nodes = self.page.locator(
            "//div[contains(@class, 'with-icon-right') and button[contains(@class, 'construct')]]"
        )

        for node in self.iter_locator(buildings_nodes):
            name = node.locator(".text-name-with-emo-icons").inner_text()
            description = node.locator(".menu-list-element-basic--description").inner_text()
            upgrade_button = node.locator(".menu-element--button--action")
            level = int(LEVEL_COMPILED.findall(description)[0])

            parsed_building = ParsedBuilding(name=name, level=level, upgrade_button=upgrade_button)
            upgradable_buildings[name] = parsed_building

        return upgradable_buildings

    def active_upgrades_count(self) -> int:
        locator = self.page.locator(
            "//div[contains(@class, 'with-icon-right') and button[contains(@class, 'finish')]]"
        )
        return locator.count()

    def habitat_upgrades(self) -> List[Building]:
        if self.active_habitat_type == HabitatType.CASTLE:
            return self.config.castle.upgrades
        if self.active_habitat_type == HabitatType.FORTRESS:
            return self.config.fortress.upgrades
        if self.active_habitat_type == HabitatType.CITY:
            return self.config.city.upgrades

        return []

    def do_upgrade(self) -> None:

        upgradable_buildings = self.upgradable_buildings()
        if not upgradable_buildings:
            self.log("no buildings to upgrade")
            return

        upgrade_steps = self.habitat_upgrades()
        if not upgrade_steps:
            self.log("unknown habitat type")
            return

        for building in upgrade_steps:
            parsed_building = upgradable_buildings.get(building.name)
            if parsed_building is None:
                continue

            while parsed_building and parsed_building.level < building.level:
                in_progress_count = self.active_upgrades_count()
                if in_progress_count >= 2:
                    self.log("no free upgrade slots")
                    return

                class_value = parsed_building.upgrade_button.get_attribute("class")
                if not class_value:
                    raise Exception("couldn't get building upgrade button status")
                if "disabled" in class_value:
                    self.log(f"no resource to upgrade {building.name}")
                    return

                parsed_building.upgrade_button.click()
                self.log(f"upgrading {parsed_building.name} to level {parsed_building.level+1}")
                self.page.wait_for_timeout(timeout=3 * SECOND)

                # refresh objects since DOM has been changed
                upgradable_buildings = self.upgradable_buildings()
                parsed_building = upgradable_buildings.get(building.name)

    def select_next_habitat(self) -> None:
        self.page.locator(".habitat-chooser--title-row .arrow-right").click()
        self.page.wait_for_timeout(SECOND)

    def under_attack(self) -> bool:
        selector = (
            "#game-bar-toggle .toggle-buttons--content__buttons [title='Castle'] .buttons--alert"
        )
        locator = self.page.locator(selector)
        if locator.count() > 0:
            return True

        return False

    def do_research(self) -> None:
        building_name = ResearchBuilding.UNIVERSITY
        if self.active_habitat_type == HabitatType.CASTLE:
            building_name = ResearchBuilding.LIBRARY

        researh_building_selector = f"#menu-section-general-container >> text={building_name}"
        self.page.locator(researh_building_selector).first.click()

        in_progress_selector = (
            "#menu-section-drill-container .menu--content-section > "
            "div:last-child .icon-research-finish"
        )
        in_progress = self.page.locator(in_progress_selector)
        if in_progress.count() > 0:
            return

        research_buttons_selector = (
            "#menu-section-drill-container .menu--content-section > "
            "div:last-child .with-icon-right > button:not(.disabled) > "
            "div:not(.icon-research-speedup):not(.icon-research-finish)"
        )
        research_buttons = self.page.locator(research_buttons_selector)
        if research_buttons.count() > 0:
            research_buttons.first.click()
            self.log("research ordered")

    def do_send_to_missions(self) -> None:
        if not self.config.missions:
            return

        if self.under_attack():
            self.log("missions skipped due to 'under attack' status", habitat_name=False)
            return

        self.click_mass_functions_button()
        self.page.locator("text=Carry out mission").click()
        self.mass_function_select_all_habitats()

        habitats_count = self.page.locator(".menu-list-element-basic--value  ").last.inner_text()
        if int(habitats_count) > 0:
            self.page.locator("text=Carry out mission").last.click()
            self.log("missions started", habitat_name=False)
        else:
            self.log("no available missions", habitat_name=False)

        self.click_mass_functions_button()
        self.page.wait_for_timeout(timeout=SECOND)

    def mass_function_select_all_habitats(self) -> None:
        selectors = (
            "text=/^Select all castles/",
            "text=/^Select all fortresses/",
            "text=/^Select all cities/",
        )
        for selector in selectors:
            try:
                link = self.page.wait_for_selector(selector, timeout=2 * SECOND, state="attached")
                if link:
                    link.click()
            except TimeoutError:  # already selected or does not exist
                pass

    def do_silver_barter(self) -> None:
        """
        We check expected amount of silver to start exchange resources from all castles to silver
        """

        if not self.config.silver_barter_threshold:
            return

        self.click_mass_functions_button()

        self.page.locator("text=Exchange resources").click()
        self.page.locator("text=Silver").last.click()
        try:
            link = self.page.wait_for_selector("text=Ox cart", timeout=2 * SECOND)
            if link:
                link.click()
        except TimeoutError:  # Ox cart not found
            self.log("no Ox-cart found to barter a silver", habitat_name=False)
            return

        self.mass_function_select_all_habitats()

        silver_amount = self.page.locator(".menu-list-element-basic--value  ").last.inner_text()
        if int(silver_amount) >= self.config.silver_barter_threshold:
            self.page.locator("text=Barter Silver").last.click()
            self.log("silver barter ordered", habitat_name=False)
        else:
            self.log(f"no enough expected silver to exchange: {silver_amount}", habitat_name=False)

        self.click_mass_functions_button()
        self.page.wait_for_timeout(timeout=SECOND)

    def logout(self) -> None:
        self.page.locator(".icon.icon-game.white.icon-profile").click()
        self.page.locator("text=Log out").click()

    def log(self, message: str, habitat_name=True) -> None:
        if habitat_name is True:
            message = f"[{self.active_habitat_type}]{self.active_habitat_name}: {message}"
        self.logger.info(message)

    def capture_screenshot(self, path: str) -> None:
        self.page.screenshot(path=path, full_page=True)

    def run(self) -> None:
        self.login()
        self.close_popup()

        self.update_active_habitat_name()
        first_habitat = self.active_habitat_name

        while True:
            self.click_building_list()
            self.update_habitat_type()
            self.do_upgrade()
            self.do_research()
            self.click_building_list()

            self.select_next_habitat()
            self.update_active_habitat_name()

            if self.active_habitat_name == first_habitat:
                break

        self.do_send_to_missions()
        self.do_silver_barter()

        self.logout()
