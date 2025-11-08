const mainWindow = new BrowserWindow({
  width: 400,
  height: 150,
  transparent: true, // Torna o fundo transparente
  frame: false,      // Remove as barras de título e bordas
  alwaysOnTop: true, // Garante que fique por cima de outros apps
  webPreferences: {
    nodeIntegration: true,
    ignoreMouseEvents: true 
  }

});
