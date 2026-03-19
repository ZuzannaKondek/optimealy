const categoryTranslations: Record<string, string> = {
  vegetable: 'Warzywa',
  fruit: 'Owoce',
  dairy: 'Nabiał',
  protein: 'Białko',
  grain: 'Zboża',
  spice: 'Przyprawy',
  condiment: 'Przyprawy',
  oil: 'Oleje',
  beverage: 'Napoje',
  bakery: 'Pieczywo',
  frozen: 'Mrożonki',
  snacks: 'Przekąski',
  canned: 'Konserwy',
  other: 'Inne',
};

export const translateCategory = (category?: string): string => {
  if (!category) return 'Inne';
  return categoryTranslations[category.toLowerCase()] || category;
};
