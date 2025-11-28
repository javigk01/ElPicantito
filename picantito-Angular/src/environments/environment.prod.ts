// Archivo de configuración de entorno para producción (Vercel)
// IMPORTANTE: 
// - apiUrl: URL de ngrok (cambia cada vez que reinicias ngrok)
// - chatbotAdminUrl y chatbotUserUrl: URLs permanentes de Streamlit Cloud

export const environment = {
  production: true,
  apiUrl: 'https://pseudoeconomical-deploringly-kizzy.ngrok-free.dev',
  // TODO: Reemplazar con tus URLs reales de Streamlit Cloud después del despliegue
  chatbotAdminUrl: 'https://elpicantito-chatbot.streamlit.app/',
  chatbotUserUrl: 'https://elpicantito-chatbotcito.streamlit.app/'
};
