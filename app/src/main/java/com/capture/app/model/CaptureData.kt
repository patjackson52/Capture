package com.capture.app.model

import android.net.Uri

/**
 * Represents a single capture — text, files, or both.
 * This is the in-memory representation before saving.
 */
data class CaptureData(
    val text: String = "",
    val tags: List<String> = emptyList(),
    val attachments: List<Attachment> = emptyList(),
    val source: CaptureSource = CaptureSource.Direct
)

data class Attachment(
    val uri: Uri,
    val mimeType: String?,
    val displayName: String?
)

enum class CaptureSource(val label: String) {
    Direct("direct"),
    Share("share"),
    ProcessText("text-selection")
}
