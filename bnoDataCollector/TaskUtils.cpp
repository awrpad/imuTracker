#include "TaskUtils.h"
#include <cstring>

Task::Task(char* _command, TaskBody _tb){
    this->command = _command;
    this->taskBody = _tb;
}

int Task::execute(char* input){
    return taskBody(input);
}

char* Task::getCommand(){
    return this->command;
}

TaskRepository::~TaskRepository(){
  for(int i = 0; i < this->tasks.size(); ++i){
    delete tasks[i];
  }
}

int TaskRepository::addTask(char* _command, TaskBody _tb){
    // If there is already a task with the given command, return an error
    for(int i = 0; i < this->tasks.size(); ++i){
        if(strcmp(this->tasks[i]->getCommand(), _command) == 0){
            return -16;
        }
    }

    this->tasks.push_back(new Task(_command, _tb));

    return 0;
}

Task *TaskRepository::getTask(char *_command){
    for(int i = 0; i < this->tasks.size(); ++i){
        if(strcmp(this->tasks[i]->getCommand(), _command) == 0){
            return (this->tasks[i]);
        }
    }

    return NULL;
}
