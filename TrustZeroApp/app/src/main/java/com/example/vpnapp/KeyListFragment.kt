package com.example.vpnapp

import android.app.AlertDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.vpnapp.database.AppDatabase
import com.example.vpnapp.database.PublicKeyItem
import java.security.KeyPairGenerator
import java.util.Base64

class KeyListFragment : Fragment() {

    private var keys: MutableList<PublicKeyItem> = mutableListOf()
    private val keyViewModel: KeyViewModel by viewModels {
        KeyViewModelFactory(AppDatabase.getDatabase(requireContext()).PublicKeyItemDao())
    }
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: PublicKeyAdapter
    private lateinit var generateKey: Button

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_key_list, container, false)
        generateKey = view.findViewById(R.id.generate_key)

        recyclerView = view.findViewById(R.id.recyclerViewKeys)

        setupRecyclerView()

        // Observe LiveData from the ViewModel
        keyViewModel.keys.observe(viewLifecycleOwner) { updatedKeys ->
            keys.clear() // Clear the existing list before adding new data
            keys.addAll(updatedKeys) // Add the updated data
            adapter.notifyDataSetChanged() // Notify adapter of data change
        }

        // Load all keys initially (this is where the data fetch happens)
        keyViewModel.getAllKeys()

        generateKey.setOnClickListener {
            val keyGen = KeyPairGenerator.getInstance("RSA")
            keyGen.initialize(2048)
            val keyPair = keyGen.generateKeyPair()
            val newKey = PublicKeyItem(keyPair = keyPair)
            keyViewModel.insertPublicKeyItem(newKey)
        }

        return view
    }

    private fun setupRecyclerView() {

        adapter = PublicKeyAdapter(keys) { keyItem ->
            showKeyOptionsDialog(keyItem)
        }

        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = adapter
    }

    private fun showKeyOptionsDialog(keyItem: PublicKeyItem) {
        var options = arrayOf("Use", "Update", "Delete")
        if(keyItem.isInUse) {
            options = arrayOf("Deselect", "Update", "Delete")
        }
        AlertDialog.Builder(requireContext())
            .setTitle("Select an Option")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> { // Use
                        // Mark this key as in use and update the RecyclerView
                        if (!keyItem.isInUse) {
                            keys.forEach {
                                if(it.isInUse != false) {
                                    it.isInUse = false
                                    keyViewModel.updatePublicKeyItem(it)
                                }
                            } // Clear previous selection
                            keyItem.isInUse = true
                            keyViewModel.updatePublicKeyItem(keyItem)
                        } else {
                            keyItem.isInUse = false
                            keyViewModel.updatePublicKeyItem(keyItem)
                        }
                        adapter.notifyDataSetChanged()
                    }
                    1 -> { // Update
                        // Perform update logic here
                        showSignaturesDialog(keyItem)
                    }
                    2 -> { // Delete
                        // Remove the selected key from the list
                        val position = keys.indexOf(keyItem)
                        if (position != -1) {
                            keyViewModel.deletePublicKeyItem(keys[position])
                            keys.removeAt(position) // Remove the item from the list
                            adapter.notifyItemRemoved(position) // Notify the adapter about item removal
                        }
                        Toast.makeText(requireContext(), "Deleted ${Base64.getEncoder().encodeToString(keyItem.keyPair.public.encoded)}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            .show()
    }

    private fun showSignaturesDialog(keyItem: PublicKeyItem) {

        // Create a custom layout for the dialog
        val dialogView =
            LayoutInflater.from(requireContext()).inflate(R.layout.sigantures_list, null)
        val recyclerView: RecyclerView = dialogView.findViewById(R.id.recycler_view_signatures)

        // Set up the adapter for signatures
        val adapter = SignatureAdapter(keyItem.getSignaturesList()) { signature ->
            // Remove the selected signature from the list
            removeSignature(keyItem, signature, keyViewModel)
            adapter.notifyDataSetChanged()
            Toast.makeText(
                requireContext(),
                "Deleted signature: ${signature.signatureText}",
                Toast.LENGTH_SHORT
            ).show()
        }
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = adapter

        // Show the dialog
        AlertDialog.Builder(requireContext())
            .setTitle("Signatures for Key")
            .setView(dialogView)
            .setPositiveButton("Close") { dialog, _ -> dialog.dismiss() }
            .show()
    }

    private fun removeSignature(publicKeyItem: PublicKeyItem, signature: Signature, viewModel: KeyViewModel) {
        val currentSignatures = publicKeyItem.getSignaturesList()
        currentSignatures.remove(signature) // Remove the specific signature
        publicKeyItem.updateSignatures(currentSignatures) // Update JSON string

        // Update in database
        viewModel.updateSignatures(publicKeyItem.id, currentSignatures)
    }
}