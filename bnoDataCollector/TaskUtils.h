#ifndef TASK_UTILS_INCLUDED
#define TASK_UTILS_INCLUDED

#include <vector>

typedef int (*TaskBody)(char*);

class Task{
    char* command;
    TaskBody taskBody;

    public:
    Task(char* _command, TaskBody _tb);
    int execute(char* input);
    char* getCommand();
};

class TaskRepository{
    std::vector<Task*> tasks; //This will be a list for now but later it could changed to something faster

    public:
    ~TaskRepository();
    int addTask(char* _command, TaskBody _tb);
    Task *getTask(char* _command);
};



#endif
