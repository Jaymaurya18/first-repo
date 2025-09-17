#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node *next;
};

struct Node *create(struct Node *head) {
    int c;
    struct Node *p, *q = NULL; // Initialize q to NULL

    do {
        p = (struct Node *)malloc(sizeof(struct Node));
        printf("Enter data: ");
        scanf("%d", &p->data);
        p->next = NULL;

        if (head == NULL) {
            head = p; // Set the head to the first node
            q = p;    // Initialize q to the first node
        } else {
            q->next = p; // Link the new node to the end
            q = p;       // Move q to the new last node
        }

        printf("Want to continue (0 to end and 1 to continue)? ");
        scanf("%d", &c);
    } while (c != 0);

    return head;
}
struct Node *insert_begin(struct Node *head) {
    struct Node *p, *new_node = (struct Node *)malloc(sizeof(struct Node));
    
    printf("Enter the new data: ");
    scanf("%d", &new_node->data);
    new_node->next = head;
    head=new_node;
    

        return head;
    }

    
   




struct Node *insert_last(struct Node *head) {
    struct Node *p, *new_node = (struct Node *)malloc(sizeof(struct Node));
    
    printf("Enter the new data: ");
    scanf("%d", &new_node->data);
    new_node->next = NULL;

    if (head == NULL) {
        return new_node; // If the list is empty, new node becomes the head
    }

    p = head;
    while (p->next != NULL) {
        p = p->next; // Traverse to the last node
    }
    p->next = new_node; // Link the new node at the end
    return head;
}

void print_list(struct Node *head) {
    struct Node *p = head;
    while (p != NULL) {
        printf("%d ", p->data);
        p = p->next;
    }
    printf("\n");
}

int main() {
    struct Node *head = NULL;

    head = create(head);
    printf("The list before insertion:\n");
    print_list(head);
    
    head = insert_begin(head);
    printf("The list after insertion:\n");
    print_list(head);

    head = insert_last(head);
    printf("The list after insertion:\n");
    print_list(head);

    return 0;
}
