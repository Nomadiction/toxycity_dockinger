import streamlit as st
import requests

# Конфигурация страницы
st.set_page_config(
    page_title="MedTox - Анализ токсичности лекарств",
    page_icon="💊"
)

# Заголовок
st.title("💊 MedTox - Анализ токсичности лекарств")

# Настройки
backend_url = "http://localhost:8000"
max_results = 10    # количество статей за один запрос

# Списки для выбора
PRESET_DRUGS = ["Aspirin", "Ibuprofen", "Paracetamol", "Metformin", "Warfarin"]
PRESET_DISEASES = ["Diabetes mellitus", "Hypertension", "Peptic ulcer disease", "Heart failure", "Chronic kidney disease"]

# Основной интерфейс
st.header("🔍 Поиск токсичности")

# Выбор лекарства
drug = st.selectbox("Выберите лекарство:", PRESET_DRUGS)

# Выбор болезни  
disease = st.selectbox("Выберите болезнь:", PRESET_DISEASES)

# Кнопка поиска
if st.button("🔍 Найти информацию о токсичности", type="primary"):
    with st.spinner("Ищем информацию..."):
        try:
            # Запрос к бэкенду
            response = requests.get(
                f"{backend_url}/toxicity",
                params={
                    "drug": drug,
                    "disease": disease,
                    "retmax": max_results
                },
                timeout=60  # timeout запроса
            )
            
            # Проверка статуса запроса
            if response.status_code == 200:
                data = response.json()
                
                # Результаты
                st.success(f"✅ Найдено {len(data['results'])} статей")
                
                # Информация
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💊 Лекарство", drug)
                with col2:
                    st.metric("🏥 Болезнь", disease)
                
                # Статьи 
                if data['results']:
                    st.subheader("📚 Найденные статьи")
                    for i, article in enumerate(data['results'], 1): 
                        st.write(f"**{i}.** {article.get('title', 'Без заголовка')}") 
                        st.write(f"   Журнал: {article.get('journal', 'Не указан')}")
                        st.write(f"   Дата: {article.get('pubdate', 'Не указана')}")
                        st.write("---")
                else:
                    st.warning("⛔ Статьи не найдены")
                
                # Анализ риска токсичности
                results_count = len(data['results'])
                if results_count >= 8:
                    st.error("☢️ **Высокий риск токсичности**")
                elif results_count >= 4:
                    st.warning("⚠️ **Средний риск токсичности**")
                elif results_count >= 1:
                    st.success("✅ **Низкий риск токсичности**")
                else:
                    st.info("**Недостаточно данных**")
                    
            else:
                st.error(f"❌ Ошибка сервера: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка подключения: {e}")
        except Exception as e:
            st.error(f"Ошибка: {e}")

# Информация о системе 
st.sidebar.header("ℹ️ О системе")
st.sidebar.info("""
**MedTox** - система анализа токсичности лекарств.

**Источники данных:**
- PubMed (научные статьи)
- PubChem (химические соединения)

**Как использовать:**
1. Выберите лекарство и болезнь
2. Нажмите кнопку поиска
3. Просмотрите результаты
""")
