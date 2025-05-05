### **1. `ragformatter.py`**

* **What It Does**:

  * This script fetches a **sitemap** of a website (like Pinecone's docs) and identifies the pages to crawl.
  * It then **triggers a web scraping tool** (Apify) to download the content of these pages.
  * After that, it triggers the next step in your process (the cleaning part).
* **When to Run**:

  * This script is generally run **first**, when you want to scrape a website's content and prepare it for processing.
  * If you ever need to **fetch new content** from a site, you'd run this.

---

### **2. `clean_json_chunks.py`**

* **What It Does**:

  * After getting the raw data from the scraping process, this script **cleans up the data**. It removes unnecessary elements like images, HTML tags, and unwanted metadata.
  * It ensures the data is ready to be processed in the next steps, by **simplifying the content** and retaining only the essential parts (like the actual text content and metadata).
* **When to Run**:

  * This script runs **after fetching the data** and cleaning it for further use.
  * If you already have raw data and just need to clean it up, you can run this script directly.

---

### **3. `split_large_json_files.py`**

* **What It Does**:

  * Sometimes the data you're processing is **too large** to handle in one go. This script takes the cleaned data and **splits it** into smaller, manageable files (under 50MB).
  * This helps in processing and storing the data more efficiently for later steps (like embedding).
* **When to Run**:

  * After cleaning the data. If the cleaned file is too large, you run this script to **split it** into smaller chunks for easier processing.

---

### **4. `inject_titles_from_source.py`**

* **What It Does**:

  * This script **adds titles** to your data, which are often missing in the cleaned chunks.
  * It uses information from the **source URL** or the filename to automatically add titles.
* **When to Run**:

  * After splitting, when your chunks are ready, and you want to ensure that each chunk has a meaningful title for later steps (like embedding).

---

### **5. `validate_json_output.py`**

* **What It Does**:

  * This script makes sure that the **output JSON is valid**. It checks that the data structure is correct and ensures that the necessary fields (like `source`, `content`, and `metadata`) are present.
  * If anything is wrong, it **stops the process** and lets you know what went wrong.
* **When to Run**:

  * You run this after splitting and injecting titles, just before you proceed with embedding or storing the data.

---

### **6. `filter_chunks.py` (Optional)**

* **What It Does**:

  * This script removes **unnecessary content** or "boilerplate" from the chunks. For example, it might strip out headers, footers, or other repetitive content that isn't useful for your model.
* **When to Run**:

  * This is an **optional step** that you can use before you finish the pipeline. It's useful if you want to **fine-tune** the data before embedding.

---

### **7. `split_ready_for_customgpt.py`**

* **What It Does**:

  * This script prepares the cleaned data for use with a **custom GPT model**. It formats the data so it can be uploaded into the model or database for semantic search and other use cases.
* **When to Run**:

  * This is the **final step**. After the data is cleaned, split, and validated, you run this script to **prepare the data for embedding or further use** in a model.

---

### **Suggested Log File Setup**

To track the **progress** of the pipeline and **log where it last succeeded**, you can use a **log file** to keep a record of each step. Here's an outline of what you can do:

1. **Create a Log File**:
   You can create a simple text or JSON log file, such as `pipeline_log.txt`, and append to it at each step.

2. **Add Logging in Each Script**:
   Each script should write to the log file when it successfully completes its task or encounters an error. For example:

   ```python
   import logging

   # Configure logging
   logging.basicConfig(filename='pipeline_log.txt', level=logging.INFO)

   # Example of logging a success message
   logging.info("Successfully cleaned data at step 2: clean_json_chunks.py")
   ```

3. **Log the Progress**:
   You can add log entries to track the progress after each major step in the pipeline, like this:

   * **Step 1: Scraping completed.**
   * **Step 2: Data cleaned successfully.**
   * **Step 3: Data split into chunks.**
   * **Step 4: Titles injected.**
   * **Step 5: Validation passed.**
   * **Step 6: Data ready for custom GPT model.**

4. **Read the Log File**:
   Whenever you run the pipeline, you can check the `pipeline_log.txt` file to see where the last successful run was and where it failed (if applicable).

---

### **Where to Start If You Need to Run a File**:

* **Start from `ragformatter.py`** if you need to fetch new data from a site.
* **Start from `clean_json_chunks.py`** if you have already scraped data but need to clean it.
* **Start from `split_large_json_files.py`** if your cleaned data is too large and needs to be split.
* **Start from `inject_titles_from_source.py`** if your data chunks need titles.
* **Start from `validate_json_output.py`** if you want to make sure your final data is properly structured.
* **Start from `split_ready_for_customgpt.py`** if you're preparing your final data for embedding or use in a custom GPT.

### **Common Errors and Solutions**

1. **HTTP Errors (e.g., 400 Bad Request)**
   - **Cause**: This usually indicates a malformed request or missing required parameters.
   - **Solution**: Check the payload being sent to the API. Ensure all required fields are included and correctly formatted.

2. **File Not Found Errors**
   - **Cause**: The script is trying to access a file that doesn't exist.
   - **Solution**: Verify the file paths and ensure the files are present in the expected directories.

3. **JSON Decode Errors**
   - **Cause**: The script is attempting to parse an invalid JSON file.
   - **Solution**: Validate the JSON file format. Use a JSON validator tool to check for syntax errors.

4. **Memory Errors**
   - **Cause**: Processing large files can lead to memory exhaustion.
   - **Solution**: Split large files into smaller chunks using the `split_large_json_files.py` script.

### **Debugging Tips**

1. **Enable Debug Logging**
   - Modify the logging level to `DEBUG` in the `config.py` to get more detailed logs.
   - Example: `logging.basicConfig(level=logging.DEBUG)`

2. **Use Print Statements**
   - Temporarily add print statements to check variable values and flow of execution.

3. **Check Log Files**
   - Review the `pipeline_log.txt` for a history of script executions and errors.

### **Best Practices**

1. **Version Control**
   - Use Git to track changes and manage different versions of your scripts.

2. **Environment Management**
   - Use virtual environments to manage dependencies and avoid conflicts.

3. **Regular Backups**
   - Regularly back up your data and scripts to prevent data loss.

4. **Code Reviews**
   - Conduct code reviews to catch potential issues early and improve code quality.

### **Performance Optimization**

1. **Optimize Data Processing**
   - Use efficient data structures and algorithms to handle large datasets.

2. **Parallel Processing**
   - Consider using parallel processing to speed up data processing tasks.

3. **Resource Monitoring**
   - Monitor system resources to identify bottlenecks and optimize performance.

### **Contact Support**

- If you encounter issues that you cannot resolve, consider reaching out to the support team or community forums for assistance.


