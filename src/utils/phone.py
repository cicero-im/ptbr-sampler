class PhoneNumber:
    formats = (
        '(0##) #### ####',
        '## ####-####',
    )

    msisdn_formats = ('##9########',)

    cellphone_formats = (
        '## 9#### ####',
        '## 9 #### ####',
        '(0##) 9#### ####',
        '(##) 9#### ####',
        '(##) 9 #### ####',
    )

    commercial_phones_formats = (
        '0300 ### ####',
        '0800 ### ####',
        '0900 ### ####',
        '0300-###-####',
        '0500-###-####',
        '0800-###-####',
        '0900-###-####',
    )

    services_phones_formats = (
        '100',
        '128',
        '151',
        '152',
        '153',
        '156',
        '180',
        '181',
        '185',
        '188',
        '190',
        '191',
        '192',
        '193',
        '194',
        '197',
        '198',
        '199',
    )

    def cellphone_number(self) -> str:
        pattern: str = self.random_element(self.cellphone_formats)
        return self.numerify(self.generator.parse(pattern))

    def service_phone_number(self) -> str:
        pattern: str = self.random_element(self.services_phones_formats)
        return self.numerify(self.generator.parse(pattern))
