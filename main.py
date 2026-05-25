"
App nativa para identificar llamadas en Colombia
- Intercepta llamadas entrantes automáticamente
- Consulta tu API en Render
- Muestra notificación con información del número
"
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock
from kivy.logger import Logger
import requests
import json

# Intentar importar permisos de Android (solo funciona en dispositivo real)
try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, cast
    from android.broadcast import BroadcastReceiver
    HAS_ANDROID = True
    Logger.info("Android: Permisos disponibles")
except ImportError:
    HAS_ANDROID = False
    Logger.warning("Android: Modo prueba - sin permisos reales")

# Clase para detectar llamadas (solo Android)
if HAS_ANDROID:
    class CallReceiver(BroadcastReceiver):
        def onReceive(self, context, intent):
            if intent.getAction() == 'android.intent.action.PHONE_STATE':
                TelephonyManager = autoclass('android.telephony.TelephonyManager')
                state = intent.getStringExtra(TelephonyManager.EXTRA_STATE)
                number = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER)
                
                if state == TelephonyManager.EXTRA_STATE_RINGING and number:
                    Logger.info(f"Llamada entrante detectada: {number}")
                    app = MDApp.get_running_app()
                    Clock.schedule_once(lambda dt: app.identify_call(number), 0)

KV = '''
ScreenManager:
    MainScreen:
        name: 'main'
    HistoryScreen:
        name: 'history'

<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.95, 0.95, 0.95, 1
        
        MDTopAppBar:
            title: "ID Llamadas Colombia"
            elevation: 2
            md_bg_color: 0.667, 0.439, 0.933, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["history", lambda x: app.show_history()]]
            
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            size_hint_y: None
            height: dp(450)
            pos_hint: {'center_x': 0.5}
            
            MDLabel:
                text: "🔍 Identificador de llamadas"
                halign: "center"
                font_style: "H5"
                size_hint_y: None
                height: dp(50)
                
            MDLabel:
                id: status_label
                text: "Protección activa"
                halign: "center"
                theme_text_color: "Secondary"
                
            MDTextField:
                id: phone_input
                hint_text: "Número colombiano"
                helper_text: "Ej: 3001234567"
                helper_text_mode: "on_focus"
                size_hint_x: 1
                
            MDRaisedButton:
                text: "Identificar"
                md_bg_color: 0.667, 0.439, 0.933, 1
                size_hint_x: 1
                on_release: app.identify_number()
                
            MDRectangleFlatButton:
                text: "Permisos de llamadas" if HAS_ANDROID else "Modo prueba"
                size_hint_x: 1
                on_release: app.request_permissions()
                
        MDLabel:
            id: result_label
            text: ""
            halign: "center"
            size_hint_y: None
            height: dp(200)

<HistoryScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Historial"
            elevation: 2
            md_bg_color: 0.667, 0.439, 0.933, 1
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            
        MDList:
            id: history_list
'''

class MainScreen(Screen):
    pass

class HistoryScreen(Screen):
    pass

class CallerIDApp(MDApp):
    API_URL = "https://caller-id-colombia.onrender.com"
    
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.history = []
        return Builder.load_string(KV)
    
    def on_start(self):
        if HAS_ANDROID:
            Clock.schedule_once(lambda dt: self.request_permissions(), 1)
            self.register_call_receiver()
    
    def register_call_receiver(self):
        if HAS_ANDROID:
            try:
                from android import activity
                receiver = CallReceiver()
                intent_filter = autoclass('android.content.IntentFilter')
                filter_obj = intent_filter()
                filter_obj.addAction('android.intent.action.PHONE_STATE')
                activity.PythonActivity.registerReceiver(receiver, filter_obj)
                Logger.info("Android: Call receiver registered")
            except Exception as e:
                Logger.error(f"Android: Error registering receiver: {e}")
    
    def request_permissions(self, *args):
        if HAS_ANDROID:
            perms = [Permission.READ_PHONE_STATE, Permission.PROCESS_OUTGOING_CALLS]
            request_permissions(perms)
            Snackbar(text="✅ Permisos concedidos", duration=2).open()
            self.root.get_screen('main').ids.status_label.text = "Protección activa ✓"
    
    def identify_call(self, phone):
        """Identifica una llamada entrante automáticamente"""
        self.identify_number(phone, is_call=True)
    
    def identify_number(self, phone=None, is_call=False):
        if phone is None:
            phone = self.root.get_screen('main').ids.phone_input.text
        
        if not phone:
            if not is_call:
                Snackbar(text="Ingresa un número").open()
            return
        
        result_label = self.root.get_screen('main').ids.result_label
        
        if is_call:
            result_label.text = "📞 Llamada detectada... Consultando..."
        else:
            result_label.text = "🔍 Buscando..."
        
        try:
            response = requests.post(
                f"{self.API_URL}/identify",
                json={"phone": phone},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('valid'):
                    riesgo = data.get('spam_risk', 'low')
                    if riesgo == 'high':
                        icono = "🔴"
                        mensaje = "¡POSIBLE SPAM!"
                    elif riesgo == 'medium':
                        icono = "🟠"
                        mensaje = "Precaución"
                    else:
                        icono = "🟢"
                        mensaje = "Seguro"
                    
                    resultado = f"""
{icono} {mensaje}

📞 {data.get('national', 'N/A')}
📡 {data.get('carrier', 'Desconocido')}
📍 {data.get('location', 'Colombia')}
📊 Reportes: {data.get('reports', 0)}
"""
                    result_label.text = resultado
                    
                    if is_call:
                        Snackbar(text=f"📞 {phone[:10]} - {data.get('carrier', '?')}", duration=3).open()
                    
                    self.save_to_history(phone, data)
                else:
                    result_label.text = f"❌ {data.get('error', 'Número inválido')}"
            else:
                result_label.text = "❌ Error de conexión"
                
        except requests.exceptions.ConnectionError:
            result_label.text = "❌ Sin conexión a internet"
        except Exception as e:
            result_label.text = f"❌ Error: {str(e)}"
    
    def save_to_history(self, phone, data):
        import time
        self.history.insert(0, {
            'phone': phone,
            'carrier': data.get('carrier', 'Desconocido'),
            'risk': data.get('spam_risk', 'low'),
            'time': time.strftime("%H:%M")
        })
        self.history = self.history[:20]
    
    def show_history(self):
        history_screen = self.root.get_screen('history')
        history_list = history_screen.ids.history_list
        history_list.clear_widgets()
        
        for item in self.history:
            from kivymd.uix.list import OneLineListItem
            icon = "🔴" if item['risk'] == 'high' else "🟠" if item['risk'] == 'medium' else "🟢"
            history_list.add_widget(
                OneLineListItem(
                    text=f"{icon} {item['phone']} - {item['carrier']} - {item['time']}"
                )
            )
        
        self.root.current = 'history'
    
    def go_back(self):
        self.root.current = 'main'

if __name__ == '__main__':
    CallerIDApp().run()
