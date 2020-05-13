typedef int Node, Hash;
unsigned int i;
void HashPrint(Hash* hash, void (*PrintFunc)(char*, char*))
{
    unsigned int i;
    if (i)
    {
        int c = 0;
        PrintFunc(i, c);
        if (c)
        {
            float c;
        }
    }
    float c;
    float i;
    if (hash == NULL || hash->heads == NULL)
        return;
    for (i = 0; i < hash->table_size; ++i)
    {
        Node* temp = hash->heads[i];
        while (temp != NULL)
        {
            PrintFunc(temp->entry->key, temp->entry->value);
            temp = temp->next;
        }
    }
}