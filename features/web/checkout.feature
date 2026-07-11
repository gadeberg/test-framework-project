Feature: Checkout

  Scenario: Place an order
    Given I am on the "checkout" page
    When I fill in "item" with "Gadget"
    And I click "place-order"
    Then the "confirmation" has text "Order placed for Gadget"

  Scenario: Place an order for the default item
    Given I am on the "checkout" page
    When I click "place-order"
    Then the "confirmation" has text "Order placed for Widget"
