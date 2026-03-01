

# class ZaDarmoException(Exception):
#     pass

# class Danie:

#     def __init__(self, nazwa: str, cena:float, skladniki:list[str]):

#         self.nazwa = nazwa
#         self.cena = cena
#         self.skladniki = skladniki
#         self.promocja = 0

#     def ustal_promocje(self, wartosc_obnizki: float):
        
#         if wartosc_obnizki == 1:
#             raise ZaDarmoException("Wartosc obnizki nie moze byc wieksza od ceny dania")
        
#         self.promocja = wartosc_obnizki

#     def __str__(self) -> str:
#         return f"{self.nazwa}, {self.cena * (1 - self.promocja)} zl, {self.skladniki}, obnizka:{self.promocja * 100}%"
        

# f = Danie("Pizza", 100, ["skladnik1", "skladnik2", "skladnik3"])
# f.ustal_promocje(0.5)

# print(f)







import sys
import time
import os


# ============================================================
# EXAMPLE 1: Reading Large Files (BEST USE CASE)
# ============================================================

def read_file_into_list(filename: str) -> list[str]:
    """
    BAD: Loads entire file into memory at once.
    Problem: If file is 10GB, you need 10GB of RAM!
    """
    print("  [List] Loading entire file into memory...")
    with open(filename, 'r') as f:
        lines = f.readlines()
    print(f"  [List] Loaded {len(lines)} lines into memory")
    return lines


def read_file_generator(filename: str):
    """
    GOOD: Yields one line at a time.
    Memory usage: Only one line in memory at a time!
    """
    print("  [Generator] Opening file (not loading into memory)...")
    with open(filename, 'r') as f:
        for line_num, line in enumerate(f, 1):
            print(f"  [Generator] Yielding line {line_num}")
            yield line.strip()
    print("  [Generator] File processing complete")


# ============================================================
# EXAMPLE 2: Infinite Sequences
# ============================================================

def fibonacci_list(n: int) -> list[int]:
    """
    BAD: Must specify limit upfront, stores all values.
    """
    fib = [0, 1]
    for _ in range(n - 2):
        fib.append(fib[-1] + fib[-2])
    return fib


def fibonacci_generator():
    """
    GOOD: Infinite sequence! No need to know the limit.
    Generates values on demand forever.
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# ============================================================
# EXAMPLE 3: Data Processing Pipeline
# ============================================================

def process_orders_with_lists(orders: list[dict]) -> list[dict]:
    """
    BAD: Creates intermediate lists at each step.
    Memory: 3x the original data!
    """
    # Step 1: Filter high-value orders
    high_value = [o for o in orders if o['amount'] > 1000]
    
    # Step 2: Add discount
    with_discount = [
        {**o, 'final_price': o['amount'] * 0.9}
        for o in high_value
    ]
    
    # Step 3: Format for output
    formatted = [
        f"Order #{o['id']}: ${o['final_price']:.2f}"
        for o in with_discount
    ]
    
    return formatted


def filter_high_value(orders):
    """Generator: Filter high-value orders"""
    for order in orders:
        if order['amount'] > 1000:
            yield order


def add_discount(orders):
    """Generator: Add 10% discount"""
    for order in orders:
        yield {**order, 'final_price': order['amount'] * 0.9}


def format_output(orders):
    """Generator: Format for display"""
    for order in orders:
        yield f"Order #{order['id']}: ${order['final_price']:.2f}"


def process_orders_with_generators(orders: list[dict]):
    """
    GOOD: Chains generators - no intermediate lists!
    Memory: Only ONE order in memory at a time through the pipeline.
    """
    return format_output(add_discount(filter_high_value(orders)))


# ============================================================
# EXAMPLE 4: Batch Processing
# ============================================================

def chunk_data_list(data: list, chunk_size: int) -> list[list]:
    """
    BAD: Creates list of lists (duplicates memory).
    """
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i:i + chunk_size])
    return chunks


def chunk_data_generator(data: list, chunk_size: int):
    """
    GOOD: Yields one chunk at a time.
    Use case: Processing API requests in batches.
    """
    for i in range(0, len(data), chunk_size):
        print(f"  [Generator] Yielding chunk starting at index {i}")
        yield data[i:i + chunk_size]


# ============================================================
# DEMONSTRATIONS
# ============================================================

if __name__ == "__main__":
    
    print("="*70)
    print("EXAMPLE 1: Reading Large Files (KILLER USE CASE)")
    print("="*70)
    
    # Create a test file
    test_file = "large_log.txt"
    print(f"\nCreating test file with 10 lines...")
    with open(test_file, 'w') as f:
        for i in range(100000):
            f.write(f"Log entry #{i+1}: Some data here\n")
    
    print("\n--- Method 1: Load entire file into list ---")
    lines = read_file_into_list(test_file)
    print(f"Memory used by list: {sys.getsizeof(lines)} bytes")
    print(f"Processing first 3 lines only:")
    for line in lines[:3]:
        print(f"  Processing: {line.strip()}")
    print("Problem: All 10 lines were loaded even though we used only 3!")
    
    print("\n--- Method 2: Use generator ---")
    line_gen = read_file_generator(test_file)
    print(f"Memory used by generator: {sys.getsizeof(line_gen)} bytes")
    print(f"Processing first 3 lines only:")
    for i, line in enumerate(line_gen):
        if i >= 3:
            break
        print(f"  Processing: {line}")
    print("Benefit: Only 3 lines were read from disk and held in memory!")
    
    # Cleanup
    os.remove(test_file)
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Infinite Sequences")
    print("="*70)
    
    print("\nWith list - must specify limit:")
    fib_list = fibonacci_list(10)
    print(f"First 10 Fibonacci numbers: {fib_list}")
    print(f"Memory: {sys.getsizeof(fib_list)} bytes")
    
    print("\nWith generator - can be infinite!")
    fib_gen = fibonacci_generator()
    print("Taking first 10 from infinite sequence:")
    first_10 = []
    for i, num in enumerate(fib_gen):
        if i >= 10:
            break
        first_10.append(num)
    print(f"First 10: {first_10}")
    
    print("\nNow let's get numbers until we exceed 1000:")
    fib_gen = fibonacci_generator()
    result = []
    for num in fib_gen:
        if num > 1000:
            break
        result.append(num)
    print(f"All Fibonacci numbers ≤ 1000: {result}")
    print("Benefit: Didn't need to know the count upfront!")
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Data Processing Pipeline")
    print("="*70)
    
    orders = [
        {'id': 1, 'amount': 500},
        {'id': 2, 'amount': 1500},
        {'id': 3, 'amount': 2000},
        {'id': 4, 'amount': 750},
        {'id': 5, 'amount': 3000},
    ]
    
    print("\n--- Method 1: Using lists (creates intermediate lists) ---")
    result_list = process_orders_with_lists(orders)
    print("Results:")
    for item in result_list:
        print(f"  {item}")
    print("Problem: Created 3 intermediate lists in memory")
    
    print("\n--- Method 2: Using generators (pipeline processing) ---")
    result_gen = process_orders_with_generators(orders)
    print(f"Generator pipeline created: {result_gen}")
    print("Memory used: ~200 bytes (no intermediate lists!)")
    print("\nNow consuming results (each order flows through entire pipeline):")
    for item in result_gen:
        print(f"  {item}")
    print("Benefit: One order at a time through the entire pipeline!")
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Processing")
    print("="*70)
    
    user_ids = list(range(1, 26))  # 25 users
    batch_size = 10
    
    print(f"\nProcessing {len(user_ids)} users in batches of {batch_size}")
    
    print("\n--- Method 1: Using list (all batches in memory) ---")
    batches_list = chunk_data_list(user_ids, batch_size)
    print(f"Created {len(batches_list)} batches")
    print(f"Memory: {sys.getsizeof(batches_list)} bytes")
    print("Batches:", batches_list)
    
    print("\n--- Method 2: Using generator (one batch at a time) ---")
    batches_gen = chunk_data_generator(user_ids, batch_size)
    print(f"Generator created: {batches_gen}")
    print(f"Memory: {sys.getsizeof(batches_gen)} bytes")
    print("\nProcessing batches:")
    for batch_num, batch in enumerate(batches_gen, 1):
        print(f"  Batch {batch_num}: {batch}")
        # Simulate sending batch to API
        time.sleep(0.5)
    print("Benefit: Only one batch in memory at a time during API calls!")
    
    print("\n" + "="*70)
    print("WHEN TO USE GENERATORS")
    print("="*70)
    print("""
    ✅ USE GENERATORS FOR:
    1. Reading large files (logs, CSVs, datasets)
    2. Infinite sequences (Fibonacci, primes, random data)
    3. Data pipelines (filter → transform → format)
    4. Batch processing (API requests, database operations)
    5. Streaming data from APIs or databases
    6. Tree/graph traversal
    7. When you might exit early (find first match)
    
    ❌ DON'T USE GENERATORS FOR:
    1. Small datasets that fit easily in memory
    2. When you need random access (indexing)
    3. When you need the length upfront
    4. When you need to iterate multiple times
    5. Operations requiring the full dataset (like sorting, max, min)
    """)
    print("="*70)