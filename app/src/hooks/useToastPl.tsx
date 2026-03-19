/**
 * Polish confirmation messages for toast notifications
 * Wiadomości potwierdzenia dla powiadomień toast
 */

export const ToastMessages = {
  // General / Ogólne
  saved: 'Zapisano pomyślnie',
  savedChanges: 'Zmiany zapisane',
  deleted: 'Usunięto pomyślnie',
  added: 'Dodano pomyślnie',
  updated: 'Zaktualizowano pomyślnie',

  // Diet / Dieta
  dietStarted: 'Dieta rozpoczęta',
  dietEnded: 'Dieta zakończona',
  dietUpdated: 'Dieta zaktualizowana',

  // Meal plans / Plany posiłków
  planCreated: 'Plan posiłków utworzony',
  planDeleted: 'Plan posiłków usunięty',
  planSaved: 'Plan zapisany',
  optimizationComplete: 'Optymalizacja zakończona',

  // Pantry / Spiżarnia
  itemAddedToPantry: 'Dodano do spiżarni',
  itemRemovedFromPantry: 'Usunięto ze spiżarni',
  pantryUpdated: 'Spiżarnia zaktualizowana',

  // Shopping list / Lista zakupów
  itemAddedToList: 'Dodano do listy zakupów',
  itemRemovedFromList: 'Usunięto z listy zakupów',
  listCleared: 'Lista wyczyszczona',

  // Settings / Ustawienia
  settingsSaved: 'Ustawienia zapisane',
  passwordChanged: 'Hasło zmienione',
  profileUpdated: 'Profil zaktualizowany',

  // Authentication / Autentykacja
  loggedIn: 'Zalogowano pomyślnie',
  loggedOut: 'Wylogowano pomyślnie',
  registered: 'Konto utworzone pomyślnie',

  // Errors / Błędy
  error: 'Wystąpił błąd',
  tryAgain: 'Spróbuj ponownie',
  connectionError: 'Błąd połączenia',
};

export type ToastMessageKey = keyof typeof ToastMessages;
