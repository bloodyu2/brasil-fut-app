const { app, BrowserWindow, Menu, shell } = require('electron');
const path = require('path');

// Keep a global reference to avoid garbage collection
let mainWindow;

function createWindow() {
  // Get screen dimensions
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  mainWindow = new BrowserWindow({
    width: Math.min(1400, width),
    height: Math.min(900, height),
    minWidth: 960,
    minHeight: 640,
    title: 'Brasil Fut',
    icon: path.join(__dirname, 'assets', process.platform === 'win32' ? 'icon.ico' : process.platform === 'darwin' ? 'icon.icns' : 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      // Allow localStorage to work
      partition: 'persist:brasilfut',
    },
    backgroundColor: '#080e18',
    show: false, // Don't show until ready to avoid flash
    autoHideMenuBar: true, // Hide menu bar by default (toggle with Alt)
  });

  // Load the game HTML
  const gameFile = path.join(__dirname, 'brasil-fut.html');
  mainWindow.loadFile(gameFile);

  // Show window when ready to avoid white flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    // Focus the window
    mainWindow.focus();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links — open in browser, not in app
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  // Custom application menu
  const menuTemplate = [
    {
      label: 'Brasil Fut',
      submenu: [
        {
          label: 'Novo Jogo',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.executeJavaScript('startNewGame && startNewGame()');
          }
        },
        { type: 'separator' },
        {
          label: 'Salvar Jogo',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.executeJavaScript('saveGame && saveGame()');
          }
        },
        {
          label: 'Carregar Jogo',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.executeJavaScript('loadGame && loadGame()');
          }
        },
        { type: 'separator' },
        { role: 'quit', label: 'Sair' }
      ]
    },
    {
      label: 'Ver',
      submenu: [
        { role: 'reload', label: 'Recarregar' },
        { role: 'forceReload', label: 'Forçar Recarga' },
        { type: 'separator' },
        { role: 'toggleFullScreen', label: 'Tela Cheia' },
        { role: 'resetZoom', label: 'Zoom Original' },
        { role: 'zoomIn', label: 'Aumentar Zoom' },
        { role: 'zoomOut', label: 'Diminuir Zoom' },
        { type: 'separator' },
        { role: 'toggleDevTools', label: 'Ferramentas de Desenvolvimento' }
      ]
    },
    {
      label: 'Ajuda',
      submenu: [
        {
          label: 'Sobre Brasil Fut',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Brasil Fut',
              message: 'Brasil Fut v1.0',
              detail: 'Gerenciador de futebol moderno.\n\nDesenvolva seu clube, escale seu time e conquiste o campeonato!',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  // On macOS, add an empty first menu item (app name)
  if (process.platform === 'darwin') {
    menuTemplate.unshift({ label: app.name, submenu: [{ role: 'about' }, { type: 'separator' }, { role: 'quit' }] });
  }

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

// App event listeners
app.whenReady().then(() => {
  createWindow();

  // macOS: re-create window when dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed (except macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// Security: prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event) => {
    event.preventDefault();
  });
});
