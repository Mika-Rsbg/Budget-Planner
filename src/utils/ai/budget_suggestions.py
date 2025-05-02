"""
Module for AI-based budget suggestions.
This provides rule-based suggestions for budgeting based on user income and expenses.
"""

class BudgetSuggestionEngine:
    """
    A simple rule-based engine for budget suggestions.
    """
    
    def __init__(self):
        # Default allocation percentages based on common financial advice
        self.default_allocations = {
            "needs": 0.50,  # 50% for needs (housing, food, utilities, etc.)
            "wants": 0.30,  # 30% for wants (entertainment, dining out, etc.)
            "savings": 0.20  # 20% for savings and debt repayment
        }
        
        # Income brackets for different suggestion tiers
        self.income_brackets = [
            (0, 1500),      # Low income
            (1500, 3000),   # Medium income
            (3000, 6000),   # High income
            (6000, float('inf'))  # Very high income
        ]
        
    def get_suggestion(self, monthly_income: float, expenses: dict = None) -> dict:
        """
        Generate budget suggestions based on income and expenses.
        
        Args:
            monthly_income (float): User's monthly income
            expenses (dict, optional): Dictionary of expense categories and amounts
            
        Returns:
            dict: Budget suggestions including allocations and tips
        """
        # Determine income bracket
        bracket = self._get_income_bracket(monthly_income)
        
        # Adjust allocations based on income bracket
        allocations = self._adjust_allocations_for_bracket(bracket)
        
        # Calculate suggested amounts
        suggested_amounts = {
            category: monthly_income * percentage 
            for category, percentage in allocations.items()
        }
        
        # Generate personalized tips
        tips = self._generate_tips(monthly_income, bracket, expenses)
        
        return {
            "allocations": allocations,
            "suggested_amounts": suggested_amounts,
            "tips": tips
        }
    
    def _get_income_bracket(self, income: float) -> int:
        """Determine which income bracket the user falls into."""
        for i, (lower, upper) in enumerate(self.income_brackets):
            if lower <= income < upper:
                return i
        return len(self.income_brackets) - 1  # Default to highest bracket
    
    def _adjust_allocations_for_bracket(self, bracket: int) -> dict:
        """Adjust allocation percentages based on income bracket."""
        allocations = self.default_allocations.copy()
        
        # Adjust allocations based on bracket
        if bracket == 0:  # Low income
            # Prioritize needs for lower incomes
            allocations["needs"] = 0.60
            allocations["wants"] = 0.20
            allocations["savings"] = 0.20
        elif bracket == 1:  # Medium income
            # Balanced approach
            allocations["needs"] = 0.50
            allocations["wants"] = 0.30
            allocations["savings"] = 0.20
        elif bracket == 2:  # High income
            # More emphasis on savings
            allocations["needs"] = 0.45
            allocations["wants"] = 0.30
            allocations["savings"] = 0.25
        else:  # Very high income
            # Even more emphasis on savings and investments
            allocations["needs"] = 0.40
            allocations["wants"] = 0.30
            allocations["savings"] = 0.30
            
        return allocations
    
    def _generate_tips(self, income: float, bracket: int, expenses: dict = None) -> list:
        """Generate personalized financial tips based on income and expenses."""
        tips = []
        
        # General tips based on income bracket
        if bracket == 0:
            tips.append("Focus on covering essential needs first.")
            tips.append("Look for ways to increase income through skills development.")
            tips.append("Build an emergency fund of at least €500.")
        elif bracket == 1:
            tips.append("Aim for a 3-month emergency fund.")
            tips.append("Consider allocating 5-10% of income to retirement savings.")
            tips.append("Review subscriptions and recurring expenses monthly.")
        elif bracket == 2:
            tips.append("Aim for a 6-month emergency fund.")
            tips.append("Consider diversifying investments.")
            tips.append("Maximize tax-advantaged retirement accounts.")
        else:
            tips.append("Consider working with a financial advisor for investment strategies.")
            tips.append("Look into tax optimization strategies.")
            tips.append("Consider charitable giving for both impact and tax benefits.")
        
        # Add expense-specific tips if expenses are provided
        if expenses:
            # Example: If housing costs are too high
            housing_cost = expenses.get("housing", 0)
            if housing_cost > income * 0.33:
                tips.append("Your housing costs exceed 33% of income. Consider ways to reduce this expense.")
                
            # Add more expense-specific logic as needed
        
        return tips