# Тест производительности для Med-Tox backend: тестирует скорость работы и ограничения API

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
import statistics
from fastapi.testclient import TestClient
from app_backend import app, pubchem_get_cid, pubmed_search, make_pubmed_term

# Создаем тестовый клиент
client = TestClient(app)

# Тест времени ответа
def test_response_time():
    response_times = []
    
    # Делаем несколько запросов для получения среднего времени
    for i in range(3):
        start_time = time.time()
        
        response = client.get("/toxicity?drug=Aspirin&disease=Diabetes&retmax=5")
        
        end_time = time.time()
        elapsed = end_time - start_time
        response_times.append(elapsed)
        
        time.sleep(1) 
    
    # Анализируем результаты
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"Среднее время ответа: {avg_time:.2f} сек")
    print(f"Максимальное время: {max_time:.2f} сек")
    print(f"Минимальное время: {min_time:.2f} сек")
    
    # Проверяем, что время ответа разумное
    assert avg_time < 30.0  # Среднее время не должно превышать 30 секунд
    assert max_time < 60.0  # Максимальное время не должно превышать 60 секунд

# Тест производительности PubChem API
def test_pubchem_performance():
    drugs = ["Aspirin", "Ibuprofen", "Paracetamol", "Metformin", "Warfarin"]
    response_times = []
    
    for drug in drugs:
        start_time = time.time()
        cid = pubchem_get_cid(drug)
        end_time = time.time()
        
        elapsed = end_time - start_time
        response_times.append(elapsed)
        
        print(f"{drug}: {elapsed:.2f} сек, CID: {cid}")
        time.sleep(0.1) 
    
    avg_time = statistics.mean(response_times)
    print(f"Среднее время PubChem: {avg_time:.2f} сек")
    
    # PubChem должен работать быстро
    assert avg_time < 5.0

# Тест производительности PubMed API
def test_pubmed_performance():
    test_cases = [
        ("Aspirin", "Diabetes"),
        ("Ibuprofen", "Hypertension"),
        ("Metformin", "Diabetes")
    ]
    
    response_times = []
    
    for drug, disease in test_cases:
        start_time = time.time()
        
        term = make_pubmed_term(drug, disease)
        pmids = pubmed_search(term, retmax=3)
        
        end_time = time.time()
        elapsed = end_time - start_time
        response_times.append(elapsed)
        
        print(f"{drug} + {disease}: {elapsed:.2f} сек, найдено: {len(pmids)} статей")
        time.sleep(1)  # Пауза для соблюдения rate limiting
    
    avg_time = statistics.mean(response_times)
    print(f"Среднее время PubMed: {avg_time:.2f} сек")
    
    # PubMed может работать медленнее
    assert avg_time < 20.0

# Тест использования памяти
def test_memory_usage():
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  
    
    # Делаем несколько запросов
    for i in range(5):
        response = client.get("/toxicity?drug=Aspirin&disease=Diabetes&retmax=3")
        time.sleep(0.5)
    
    final_memory = process.memory_info().rss / 1024 / 1024  
    memory_increase = final_memory - initial_memory
    
    print(f"Начальная память: {initial_memory:.2f} MB")
    print(f"Конечная память: {final_memory:.2f} MB")
    print(f"Увеличение: {memory_increase:.2f} MB")
    
    # Память не должна увеличиваться критически
    assert memory_increase < 100  # Не более 100 MB

# Тест соблюдения ограничений скорости
def test_rate_limiting_compliance():
    start_time = time.time()
    
    # Делаем быстрые запросы
    for i in range(5):
        response = client.get("/toxicity?drug=Aspirin&disease=Diabetes&retmax=2")
        time.sleep(0.1) 
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"Время для 5 запросов: {total_time:.2f} сек")
    
    # Запросы должны занимать разумное время
    assert total_time > 2.0  # Минимум 2 секунды для 5 запросов

# Тест с большим количеством результатов
def test_large_result_set():
    start_time = time.time()
    
    response = client.get("/toxicity?drug=Aspirin&disease=Diabetes&retmax=20")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    if response.status_code == 200:
        data = response.json()
        result_count = len(data["results"])
        
        print(f"Найдено {result_count} статей за {elapsed:.2f} сек")
        
        # Больше результатов должно занимать больше времени
        assert elapsed > 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

