Test sample.

Before running a test, copy the contents of either documents_pass or documents_fail folder to the documents folder of the test.

The document 1 in documents_pass and documents_fail folders are identical. The same is true for document 3. Documents 2 and 4 are slightly different. The screenshots in both folders were created using documents from documents_pass. So, two screenshots in documents_fail don't match the respective documents.

That is, if you run the documents_pass set, all tests will pass. If you run the documents_fail set, you will have fails with documents 2 and 4.

After running the update_script, the screenshots and documents must match. Then all tests will pass.
