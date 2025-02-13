package com.example.vpnapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class SignatureAdapter(
    private val signatures: List<Signature>,
    private val onDeleteClick: (Signature) -> Unit
) : RecyclerView.Adapter<SignatureAdapter.SignatureViewHolder>() {

    inner class SignatureViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val signatureTextView: TextView = itemView.findViewById(R.id.signature_text)
        val appIdentifierTextView: TextView = itemView.findViewById(R.id.app_identifier)
        val deleteButton: Button = itemView.findViewById(R.id.delete_button)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SignatureViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_signature, parent, false)
        return SignatureViewHolder(view)
    }

    override fun onBindViewHolder(holder: SignatureViewHolder, position: Int) {
        val signature = signatures[position]
        holder.signatureTextView.text = signature.signatureText
        holder.appIdentifierTextView.text = signature.appIdentifier  // Display the app identifier
        holder.deleteButton.setOnClickListener {
            onDeleteClick(signature)
        }
    }

    override fun getItemCount(): Int = signatures.size
}