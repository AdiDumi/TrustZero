import matplotlib.pyplot as plt
import numpy as np

# Define signature sizes and public key sizes in bytes
signature_sizes = {
    'RSA (2048 bits)': 256,    # RSA signature size
    'ECDSA (P-256)': 64,        # ECDSA signature size
    'EdDSA (Ed25519)': 64       # EdDSA signature size
}

public_key_sizes = {
    'RSA (2048 bits)': 256,     # RSA public key size
    'ECDSA (P-256)': 64,         # ECDSA public key size
    'EdDSA (Ed25519)': 32        # EdDSA public key size
}

# Define a range of number of signatures
num_signatures_range = np.arange(1, 81)  # From 1 to 20 signatures

# Initialize a dictionary to hold the total sizes
total_sizes = {key: [] for key in signature_sizes.keys()}

# Calculate the total size for each number of signatures
for num_signatures in num_signatures_range:
    for algo in signature_sizes.keys():
        sig_size = signature_sizes[algo]
        pub_key_size = public_key_sizes[algo]
        total_size = (num_signatures * sig_size) + pub_key_size  # Calculate total size
        total_sizes[algo].append(total_size)

# Create the plot
plt.figure(figsize=(10, 6))

for algo, sizes in total_sizes.items():
    plt.plot(num_signatures_range, sizes, marker='o', label=algo)

# Adding labels and title
plt.title('Total Size vs. Number of Signatures (Including Public Key Size)')
plt.xlabel('Number of Signatures')
plt.ylabel('Total Size (bytes)')
plt.grid(True)
plt.legend()
plt.tight_layout()

# Show the plot
plt.savefig("test2.png", format='png')
plt.show()