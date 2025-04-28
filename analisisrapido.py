def main():
    counts = []
    with open("resultado.txt", "r") as f:
        for line in f:
            line = line.strip()
            # Si la línea comienza con un dígito, se asume que es la línea con el número
            if line and line[0].isdigit():
                partes = line.split()
                try:
                    count = int(partes[0])
                    counts.append(count)
                except ValueError:
                    pass  # Si no se puede convertir, se ignora la línea

    if counts:
        promedio = statistics.mean(counts)
        # statistics.stdev calcula la desviación estándar muestral
        desviacion = statistics.stdev(counts)
        print(f"Promedio: {promedio}")
        print(f"Desviación estándar: {desviacion}")
    else:
        print("No se encontraron números en el archivo.")

if __name__ == "__main__":
    main()
